import datetime
import hashlib
import secrets

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.config import settings
from app.models import User, College, Canteen, RegistrationOtp
from app.schemas import (
    RegisterRequest, UserResponse, LoginRequest, LoginResponse, UpdateProfileRequest,
    RegistrationOtpResponse, VerifyRegistrationOtpRequest, ResendRegistrationOtpRequest,
)
from app.security import hash_password, verify_password, create_access_token, UnauthenticatedException, get_current_user_id
from app.exceptions import BadRequestException, NotFoundException
from app.security_rules import enforce_ip_account_limit

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


def normalize_phone(phone: str) -> str:
    """Normalize phone input to digits only, keeping the country code."""
    normalized = "".join(char for char in (phone or "").strip() if char.isdigit())
    if not 10 <= len(normalized) <= 15:
        raise BadRequestException("phone must include a valid country code, for example 919876543210")
    return normalized


def otp_hash(code: str) -> str:
    secret = settings.OTP_HASH_SECRET or settings.JWT_SECRET
    return hashlib.sha256(f"{code}:{secret}".encode("utf-8")).hexdigest()


async def send_registration_otp(phone: str, code: str) -> None:
    if not settings.WHATSAPP_BOT_INTERNAL_KEY:
        raise HTTPException(status_code=503, detail="WhatsApp OTP delivery is not configured")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{settings.WHATSAPP_BOT_URL.rstrip('/')}/internal/whatsapp/send-otp",
                headers={"x-internal-api-key": settings.WHATSAPP_BOT_INTERNAL_KEY},
                json={
                    "phone": phone,
                    "otp": code,
                    "expiresInMinutes": settings.OTP_EXPIRY_MINUTES,
                },
            )
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail="Unable to send WhatsApp verification code") from exc


async def create_and_send_otp(user: User, db: AsyncSession) -> None:
    code = f"{secrets.randbelow(1_000_000):06d}"
    existing = (await db.execute(select(RegistrationOtp).where(RegistrationOtp.user_id == user.id))).scalar_one_or_none()
    if existing:
        await db.delete(existing)
        await db.flush()
    db.add(RegistrationOtp(
        user_id=user.id,
        code_hash=otp_hash(code),
        expires_at=datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.OTP_EXPIRY_MINUTES),
    ))
    await db.commit()
    await send_registration_otp(user.phone, code)

@router.post("/register", response_model=RegistrationOtpResponse, status_code=201)
async def register(request: RegisterRequest, http_request: Request, db: AsyncSession = Depends(get_db)):
    """Creates a pending account and sends its WhatsApp verification code."""
    phone = normalize_phone(request.phone or "")
    async with db.begin():
        email_result = await db.execute(select(User).where(User.email == request.email))
        existing_user = email_result.scalars().first()
        if existing_user and existing_user.phone_verified:
            raise BadRequestException("A user with this email address already exists")

        roll_result = await db.execute(select(User).where(User.roll_number == request.roll_number))
        existing_roll_user = roll_result.scalars().first()
        if existing_roll_user and (not existing_user or existing_roll_user.id != existing_user.id):
            raise BadRequestException("A user with this roll number already exists")

        client_ip = http_request.client.host if http_request.client else "unknown"
        await enforce_ip_account_limit(client_ip, request.email)

        if not request.college_id or not request.preferred_canteen_id:
            raise BadRequestException("collegeId and preferredCanteenId are required")
        college = (await db.execute(select(College).where(College.id == request.college_id))).scalar_one_or_none()
        canteen = (await db.execute(select(Canteen).join(Canteen.colleges).where(
            College.id == request.college_id,
            Canteen.id == request.preferred_canteen_id,
            Canteen.is_active == True,
        ))).scalar_one_or_none()
        if not college or not canteen:
            raise BadRequestException("Selected college and canteen combination is invalid")

        if existing_user:
            existing_user.name = request.name
            existing_user.phone = phone
            existing_user.roll_number = request.roll_number
            existing_user.college = request.college
            existing_user.college_id = request.college_id
            existing_user.preferred_canteen_id = request.preferred_canteen_id
            existing_user.hashed_password = hash_password(request.password)
            existing_user.phone_verified = False
            new_user = existing_user
        else:
            # Create new User object and save to DB
            new_user = User(
                name=request.name,
                email=request.email,
                phone=phone,
                roll_number=request.roll_number,
                college=request.college,
                college_id=request.college_id,
                preferred_canteen_id=request.preferred_canteen_id,
                hashed_password=hash_password(request.password)
            )
            db.add(new_user)

        await db.flush()

    await create_and_send_otp(new_user, db)
    return RegistrationOtpResponse(
        expires_in_minutes=settings.OTP_EXPIRY_MINUTES,
        message="Verification code sent to your WhatsApp number.",
    )


@router.post("/verify-otp", response_model=LoginResponse)
async def verify_otp(request: VerifyRegistrationOtpRequest, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(User.email == request.email))).scalar_one_or_none()
    if not user or user.phone_verified:
        raise BadRequestException("No pending registration was found for this email")
    verification = (await db.execute(select(RegistrationOtp).where(RegistrationOtp.user_id == user.id))).scalar_one_or_none()
    now = datetime.datetime.utcnow()
    if not verification or verification.expires_at <= now:
        raise BadRequestException("Verification code has expired. Please register again.")
    if verification.attempts >= settings.OTP_MAX_ATTEMPTS:
        raise BadRequestException("Too many invalid attempts. Please register again.")
    if not secrets.compare_digest(verification.code_hash, otp_hash(request.otp)):
        verification.attempts += 1
        await db.commit()
        raise BadRequestException("Invalid verification code")

    user.phone_verified = True
    await db.delete(verification)
    await db.commit()
    return LoginResponse(
        access_token=create_access_token(user.id),
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post("/resend-otp", response_model=RegistrationOtpResponse)
async def resend_otp(request: ResendRegistrationOtpRequest, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(User.email == request.email))).scalar_one_or_none()
    if not user or user.phone_verified or not verify_password(request.password, user.hashed_password):
        raise BadRequestException("No pending registration was found for these credentials")
    await create_and_send_otp(user, db)
    return RegistrationOtpResponse(
        expires_in_minutes=settings.OTP_EXPIRY_MINUTES,
        message="A new verification code was sent to your WhatsApp number.",
    )


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, http_request: Request, db: AsyncSession = Depends(get_db)):
    """Authenticates user credentials and returns a signed JWT access token."""
    # Find user by email
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalars().first()
    if not user:
        raise UnauthenticatedException("Invalid email or password")

    # Verify matching hashed password
    if not verify_password(request.password, user.hashed_password):
        raise UnauthenticatedException("Invalid email or password")

    if not user.phone_verified:
        raise UnauthenticatedException("Please verify your WhatsApp number before logging in")

    client_ip = http_request.client.host if http_request.client else "unknown"
    await enforce_ip_account_limit(client_ip, request.email)

    # Increment token_version → invalidates ALL existing sessions on other devices
    user.token_version = (user.token_version or 1) + 1
    await db.commit()
    await db.refresh(user)

    # Generate token with new version embedded
    token = create_access_token(user.id, token_version=user.token_version)

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.patch("/profile", response_model=UserResponse)
async def update_profile(
    request: UpdateProfileRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Update profile details (name, phone, and optionally password)."""
    async with db.begin():
        result = await db.execute(select(User).where(User.id == current_user_id))
        user = result.scalars().first()
        if not user:
            raise NotFoundException("User not found")
        
        if request.name is not None:
            user.name = request.name
        if request.phone is not None:
            user.phone = request.phone
        if getattr(request, "roll_number", None) is not None:
            user.roll_number = request.roll_number
        if getattr(request, "college", None) is not None:
            user.college = request.college
        if request.college_id is not None:
            user.college_id = request.college_id
        if request.preferred_canteen_id is not None:
            user.preferred_canteen_id = request.preferred_canteen_id
        if request.use_roll_number_as_order_token is not None:
            user.use_roll_number_as_order_token = request.use_roll_number_as_order_token
        if request.password is not None:
            user.hashed_password = hash_password(request.password)
            
        await db.flush()
        
    # Re-retrieve to return updated state
    result = await db.execute(select(User).where(User.id == current_user_id))
    updated_user = result.scalars().first()
    return UserResponse.model_validate(updated_user)
