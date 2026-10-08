import datetime
import hashlib
import secrets
import logging
from typing import Optional, List

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.database import get_db
from app.config import settings
from app.models import User, College, Canteen, RegistrationOtp, PasswordResetOtp, UserFcmToken
from app.schemas import (
    RegisterRequest, UserResponse, LoginRequest, LoginResponse, UpdateProfileRequest,
    RegistrationOtpResponse, VerifyRegistrationOtpRequest, ResendRegistrationOtpRequest,
    RefreshRequest, RefreshResponse, DeleteAccountResponse,
    ForgotPasswordRequest, ForgotPasswordOtpResponse,
    VerifyResetOtpRequest, VerifyResetOtpResponse,
    ResetPasswordRequest, ResetPasswordResponse,
    DeviceTokenRequest, DeviceTokenResponse,
)
from app.security import (
    hash_password, verify_password, verify_password_async,
    create_access_token, create_refresh_token, hash_refresh_jti,
    create_password_reset_token, verify_password_reset_token,
    UnauthenticatedException, get_current_user_id_verified, get_current_user_id_optional, get_client_ip,
    _decode_token,
)
from app.exceptions import BadRequestException, NotFoundException
from app.security_rules import (
    enforce_ip_account_limit, rate_limit_login, rate_limit_login_by_account,
    throttle_otp_per_phone,
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
logger = logging.getLogger("onfood.auth")


# ─── Internal Helpers ──────────────────────────────────────

def normalize_phone(phone: str) -> str:
    """Normalize phone input to digits only, keeping the country code."""
    normalized = "".join(char for char in (phone or "").strip() if char.isdigit())
    if not 10 <= len(normalized) <= 15:
        raise BadRequestException("phone must include a valid country code, for example 919876543210")
    return normalized


def otp_hash(code: str) -> str:
    secret = settings.OTP_HASH_SECRET or settings.JWT_SECRET
    return hashlib.sha256(f"{code}:{secret}".encode("utf-8")).hexdigest()


def _make_token_pair(user: User) -> tuple[str, str]:
    """Return (access_token, refresh_token) for the given user."""
    access = create_access_token(user.id, token_version=user.token_version)
    refresh, _ = create_refresh_token(user.id, refresh_version=user.refresh_token_version)
    return access, refresh


async def send_registration_otp(phone: str, code: str) -> bool:
    if not settings.WHATSAPP_BOT_INTERNAL_KEY or not settings.WHATSAPP_BOT_URL:
        logging.warning(f"[DEV MODE] WhatsApp OTP delivery is not configured. Phone: {phone}, OTP: {code}")
        return False
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
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
            return True
    except httpx.HTTPStatusError as exc:
        logging.error(f"[DEV MODE] Failed to send WhatsApp verification code to {phone}: {exc} (Response: {exc.response.text}). OTP was: {code}")
        return False
    except httpx.HTTPError as exc:
        logging.error(f"[DEV MODE] Failed to send WhatsApp verification code to {phone}: {exc}. OTP was: {code}")
        return False
    except Exception as exc:
        logging.error(f"Unexpected error sending WhatsApp verification code to {phone}: {exc}. OTP was: {code}")
        return False


async def send_registration_email_otp(email: str, name: str, code: str) -> bool:
    """Send verification OTP code via Zoho SMTP email."""
    from app.email import send_email
    subject = f"Your OnFood Verification Code: {code}"
    body = (
        f"<div style='font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto; color: #333;'>"
        f"<h2 style='color: #ff6f00;'>Welcome to OnFood!</h2>"
        f"<p>Hi <b>{name or 'there'}</b>,</p>"
        f"<p>Thank you for registering. Your verification code is:</p>"
        f"<div style='background: #fff3e0; padding: 18px; text-align: center; "
        f"border-radius: 8px; margin: 18px 0; border: 1px dashed #ff9800;'>"
        f"<span style='font-size: 32px; font-weight: bold; letter-spacing: 6px; color: #e65100;'>"
        f"{code}</span></div>"
        f"<p>This code expires in <b>{settings.OTP_EXPIRY_MINUTES} minutes</b>.</p>"
        f"<p>Please enter this code in the app to complete your verification.</p>"
        f"<hr style='border: none; border-top: 1px solid #eee; margin: 24px 0;'>"
        f"<p style='color: #999; font-size: 12px;'>OnFood - Campus Food Ordering</p>"
        f"</div>"
    )
    return await send_email(to=email, subject=subject, body=body, html=True)


async def create_and_send_otp(user: User, db: AsyncSession, is_resend: bool = False) -> tuple[bool, str, str | None]:
    # Per-phone throttle: max 3 sends per hour if phone is present
    if user.phone:
        await throttle_otp_per_phone(user.phone)

    # Generate a random 6-digit code
    random_code = f"{secrets.randbelow(1_000_000):06d}"

    # Attempt to send OTP via WhatsApp first, then fallback to email
    sent = False
    delivery_channel = None

    if user.phone:
        try:
            sent = await send_registration_otp(user.phone, random_code)
            if sent:
                delivery_channel = "whatsapp"
        except Exception as exc:
            logging.warning(f"Error sending WhatsApp OTP to {user.phone}: {exc}")
            sent = False

    # If WhatsApp delivery failed (or user has no phone), fallback to email
    if not sent and user.email:
        try:
            sent = await send_registration_email_otp(user.email, user.name or "", random_code)
            if sent:
                delivery_channel = "email"
        except Exception as exc:
            logging.error(f"Error sending registration email OTP to {user.email}: {exc}")
            sent = False

    if sent:
        otp_code = random_code
        fallback_otp = None
        if delivery_channel == "whatsapp":
            masked = mask_phone(user.phone)
            message = (
                f"A new verification code was sent to your WhatsApp ({masked})."
                if is_resend
                else f"Verification code sent to your WhatsApp ({masked})."
            )
        else:
            masked = mask_email(user.email)
            message = (
                f"A new verification code was sent to your email ({masked})."
                if is_resend
                else (
                    f"WhatsApp delivery failed. Verification code sent to your email ({masked})."
                    if user.phone
                    else f"Verification code sent to your email ({masked})."
                )
            )
    else:
        # If both WhatsApp and email delivery failed, provide fallback OTP
        otp_code = random_code
        fallback_otp = otp_code
        masked = mask_email(user.email) if user.email else mask_phone(user.phone or "your phone")
        message = (
            f"Could not send verification code via WhatsApp or email to {masked}. Use verification code {fallback_otp} to complete registration."
        )

    existing = (await db.execute(
        select(RegistrationOtp).where(RegistrationOtp.user_id == user.id)
    )).scalar_one_or_none()
    if existing:
        await db.delete(existing)
        await db.flush()

    db.add(RegistrationOtp(
        user_id=user.id,
        code_hash=otp_hash(otp_code),
        expires_at=datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.OTP_EXPIRY_MINUTES),
        attempts=0,
    ))
    await db.commit()
    return sent, message, fallback_otp


def mask_phone(phone: str) -> str:
    """Mask phone number for safe display, e.g. '919876543210' -> '+91 ******3210'."""
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) < 4:
        return "****"
    prefix = "+" + digits[:-10] if len(digits) > 10 else ""
    last_four = digits[-4:]
    return f"{prefix} ******{last_four}".strip()


def mask_email(email: str) -> str:
    """Mask email for safe display, e.g. 'karthik@gmail.com' -> 'ka****ik@gmail.com'."""
    if "@" not in email:
        return "****"
    local, domain = email.rsplit("@", 1)
    if len(local) <= 2:
        masked_local = local[0] + "****"
    else:
        masked_local = local[:2] + "****" + local[-2:]
    return f"{masked_local}@{domain}"


async def find_user_by_identifier(db: AsyncSession, identifier: str) -> User | None:
    """Find a user by email or phone number."""
    cleaned = identifier.strip()
    if "@" in cleaned:
        result = await db.execute(select(User).where(User.email.ilike(cleaned)))
        return result.scalars().first()

    digits = "".join(ch for ch in cleaned if ch.isdigit())
    if not digits:
        return None

    if len(digits) >= 10:
        last_10 = digits[-10:]
        result = await db.execute(select(User).where(User.phone == digits))
        user = result.scalars().first()
        if user:
            return user
        result = await db.execute(select(User).where(User.phone.endswith(last_10)))
        return result.scalars().first()

    result = await db.execute(select(User).where(User.phone == digits))
    return result.scalars().first()


async def create_and_send_reset_otp(user: User, db: AsyncSession) -> tuple[bool, str, str | None]:
    if not user.email and not user.phone:
        raise BadRequestException("No registered email or phone found for this account. Please contact support.")

    random_code = f"{secrets.randbelow(1_000_000):06d}"

    sent = False
    delivery_channel = None

    # Try WhatsApp first if phone number is available
    if user.phone:
        try:
            sent = await send_registration_otp(user.phone, random_code)
            if sent:
                delivery_channel = "whatsapp"
        except Exception as exc:
            logging.warning(f"Failed to send password reset OTP via WhatsApp to {user.phone}: {exc}")
            sent = False

    # If WhatsApp delivery failed (or user has no phone), fallback to email
    if not sent and user.email:
        from app.email import send_email
        try:
            sent = await send_email(
                to=user.email,
                subject=f"OnFood Password Reset Code: {random_code}",
                body=(
                    f"<div style='font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto;'>"
                    f"<h2 style='color: #333;'>Password Reset</h2>"
                    f"<p>Hi <b>{user.name or 'there'}</b>,</p>"
                    f"<p>Your password reset verification code is:</p>"
                    f"<div style='background: #f5f5f5; padding: 20px; text-align: center; "
                    f"border-radius: 8px; margin: 16px 0;'>"
                    f"<span style='font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #333;'>"
                    f"{random_code}</span></div>"
                    f"<p>This code expires in <b>{settings.OTP_EXPIRY_MINUTES} minutes</b>.</p>"
                    f"<p>If you did not request this, please ignore this email.</p>"
                    f"<hr style='border: none; border-top: 1px solid #eee; margin: 24px 0;'>"
                    f"<p style='color: #999; font-size: 12px;'>OnFood - Campus Food Ordering</p>"
                    f"</div>"
                ),
                html=True,
            )
            if sent:
                delivery_channel = "email"
        except Exception as exc:
            logging.error(f"Error sending password reset email to {user.email}: {exc}")
            sent = False

    if sent:
        otp_code = random_code
        fallback_otp = None
        if delivery_channel == "whatsapp":
            masked = mask_phone(user.phone)
            message = f"Verification code sent to your WhatsApp ({masked})."
        else:
            masked = mask_email(user.email)
            message = (
                f"WhatsApp delivery failed. Verification code sent to your email ({masked})."
                if user.phone
                else f"Verification code sent to your registered email address ({masked})."
            )
    else:
        otp_code = random_code
        fallback_otp = otp_code
        message = "Failed to send verification code via WhatsApp or email. Please try again later."

    existing = (await db.execute(
        select(PasswordResetOtp).where(PasswordResetOtp.user_id == user.id)
    )).scalar_one_or_none()
    if existing:
        await db.delete(existing)
        await db.flush()

    db.add(PasswordResetOtp(
        user_id=user.id,
        code_hash=otp_hash(otp_code),
        expires_at=datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.OTP_EXPIRY_MINUTES),
        attempts=0,
    ))
    await db.commit()
    return sent, message, fallback_otp


# ─── Registration ──────────────────────────────────────────

@router.post("/register", response_model=RegistrationOtpResponse, status_code=201)
async def register(request: RegisterRequest, http_request: Request, db: AsyncSession = Depends(get_db)):
    """Creates a pending account and sends its WhatsApp verification code."""
    phone = normalize_phone(request.phone or "")
    async with db.begin():
        if not request.roll_number or not (len(request.roll_number) == 3 and request.roll_number.isdigit()):
            raise BadRequestException("College ID must be a 3-digit number (e.g. 101)")

        email_result = await db.execute(select(User).where(User.email == request.email))
        existing_user = email_result.scalars().first()
        if existing_user:
            if getattr(existing_user, "status", "active") == "hold":
                raise BadRequestException("This account is currently on hold. Please contact support.")
            if existing_user.phone_verified:
                raise BadRequestException("A user with this email address already exists")

        roll_result = await db.execute(select(User).where(User.roll_number == request.roll_number))
        existing_roll_user = roll_result.scalars().first()
        if existing_roll_user and (not existing_user or existing_roll_user.id != existing_user.id):
            if getattr(existing_roll_user, "status", "active") == "hold":
                raise BadRequestException("This college ID belongs to an account currently on hold. Please contact support.")
            raise BadRequestException("A user with this roll number already exists")

        client_ip = get_client_ip(http_request)
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

        if not settings.REQUIRE_REGISTRATION_OTP:
            new_user.phone_verified = True
            await db.commit()
            return RegistrationOtpResponse(
                verification_required=False,
                expires_in_minutes=0,
                message="Registration successful. OTP verification is not required.",
                delivery_failed=False,
                otp_failed=False,
                otp_sent=False,
                status="verified",
                fallback_otp=None,
            )

        await db.flush()

    sent, message, fallback_otp = await create_and_send_otp(new_user, db, is_resend=False)
    return RegistrationOtpResponse(
        verification_required=True,
        expires_in_minutes=settings.OTP_EXPIRY_MINUTES,
        message=message,
        delivery_failed=not sent,
        otp_failed=not sent,
        otp_sent=sent,
        status="otp_sent" if sent else "otp_failed",
        fallback_otp=fallback_otp,
    )


# ─── OTP Verification ──────────────────────────────────────

@router.post("/verify-otp", response_model=LoginResponse)
@router.post("/check-otp", response_model=LoginResponse, include_in_schema=False)
async def verify_otp(
    request: VerifyRegistrationOtpRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
):
    client_ip = get_client_ip(http_request)
    await rate_limit_login(client_ip)

    target_identifier = request.email or request.identifier or request.phone
    if not target_identifier:
        raise BadRequestException("Email, identifier, or phone is required")

    target_identifier = target_identifier.strip()
    if "@" in target_identifier:
        user = (await db.execute(select(User).where(User.email.ilike(target_identifier)))).scalar_one_or_none()
    else:
        user = await find_user_by_identifier(db, target_identifier)

    if not user:
        raise BadRequestException("No registration was found for this email or phone")
    if getattr(user, "status", "active") == "hold":
        raise BadRequestException("Account is currently on hold. Please contact support.")

    # If the user is already verified or server has OTP requirement disabled, log in directly
    if user.phone_verified or not settings.REQUIRE_REGISTRATION_OTP:
        user.phone_verified = True
        user.token_version = (user.token_version or 1) + 1
        user.refresh_token_version = (user.refresh_token_version or 1) + 1
        access_token = create_access_token(user.id, token_version=user.token_version)
        refresh_token, jti = create_refresh_token(user.id, refresh_version=user.refresh_token_version)
        user.refresh_token_hash = hash_refresh_jti(jti)
        await db.commit()
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )

    verification = (await db.execute(
        select(RegistrationOtp).where(RegistrationOtp.user_id == user.id)
    )).scalar_one_or_none()

    now = datetime.datetime.utcnow()

    if not verification or verification.expires_at <= now:
        raise BadRequestException("Verification code has expired. Please register again or request a new code.")
    if verification.attempts >= settings.OTP_MAX_ATTEMPTS:
        raise BadRequestException("Too many invalid attempts. Please request a new code.")
    if not secrets.compare_digest(verification.code_hash, otp_hash(request.otp.strip())):
        verification.attempts += 1
        await db.commit()
        raise BadRequestException("Invalid verification code")

    user.phone_verified = True
    user.token_version = (user.token_version or 1) + 1
    user.refresh_token_version = (user.refresh_token_version or 1) + 1
    if verification:
        await db.delete(verification)
    await db.flush()

    # Generate refresh token and store its JTI hash
    access_token = create_access_token(user.id, token_version=user.token_version)
    refresh_token, jti = create_refresh_token(user.id, refresh_version=user.refresh_token_version)
    user.refresh_token_hash = hash_refresh_jti(jti)
    await db.commit()

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


# ─── Resend OTP ────────────────────────────────────────────

@router.post("/resend-otp", response_model=RegistrationOtpResponse)
async def resend_otp(request: ResendRegistrationOtpRequest, db: AsyncSession = Depends(get_db)):
    clean_email = request.email.strip()
    user = (await db.execute(select(User).where(User.email.ilike(clean_email)))).scalar_one_or_none()
    if not user or not await verify_password_async(request.password, user.hashed_password):
        raise BadRequestException("No pending registration was found for these credentials")
    if getattr(user, "status", "active") == "hold":
        raise BadRequestException("Account is currently on hold. Please contact support.")

    if not settings.REQUIRE_REGISTRATION_OTP or user.phone_verified:
        user.phone_verified = True
        await db.commit()
        return RegistrationOtpResponse(
            verification_required=False,
            expires_in_minutes=0,
            message="Your account is already verified. You can log in.",
            delivery_failed=False,
            otp_failed=False,
            otp_sent=False,
            status="verified",
            fallback_otp=None,
        )

    sent, message, fallback_otp = await create_and_send_otp(user, db, is_resend=True)
    return RegistrationOtpResponse(
        verification_required=True,
        expires_in_minutes=settings.OTP_EXPIRY_MINUTES,
        message=message,
        delivery_failed=not sent,
        otp_failed=not sent,
        otp_sent=sent,
        status="otp_sent" if sent else "otp_failed",
        fallback_otp=fallback_otp,
    )


# ─── Login ─────────────────────────────────────────────────

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, http_request: Request, db: AsyncSession = Depends(get_db)):
    """Authenticates user credentials and returns a signed JWT access + refresh token pair."""
    client_ip = get_client_ip(http_request)
    # Run both rate limiters in parallel — per-IP and per-account
    await rate_limit_login(client_ip)
    await rate_limit_login_by_account(request.email)
    await enforce_ip_account_limit(client_ip, request.email)

    clean_email = request.email.strip()
    result = await db.execute(select(User).where(User.email.ilike(clean_email)))
    user = result.scalars().first()
    if not user:
        raise UnauthenticatedException("Invalid email or password")

    if not await verify_password_async(request.password, user.hashed_password):
        raise UnauthenticatedException("Invalid email or password")

    if getattr(user, "status", "active") == "hold":
        raise UnauthenticatedException("Your account is currently on hold. Please contact support.")

    if not user.phone_verified:
        if not settings.REQUIRE_REGISTRATION_OTP:
            user.phone_verified = True
            await db.commit()
        else:
            raise UnauthenticatedException("Please verify your account before logging in")

    # Bump token_version → invalidates ALL existing access tokens on other devices
    user.token_version = (user.token_version or 1) + 1
    # Bump refresh_token_version → invalidates ALL existing refresh tokens
    user.refresh_token_version = (user.refresh_token_version or 1) + 1
    await db.flush()

    access_token = create_access_token(user.id, token_version=user.token_version)
    refresh_token, jti = create_refresh_token(user.id, refresh_version=user.refresh_token_version)
    user.refresh_token_hash = hash_refresh_jti(jti)
    await db.commit()
    await db.refresh(user)

    if request.fcm_token:
        try:
            await record_user_device_token(
                db=db,
                user_id=user.id,
                fcm_token=request.fcm_token,
                device_name=request.device_name,
                platform=request.platform,
            )
        except Exception as fcm_err:
            logger.warning(f"[Login FCM] Could not register token during login: {fcm_err}")

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


# ─── Refresh ───────────────────────────────────────────────

@router.post("/refresh", response_model=RefreshResponse)
async def refresh_access_token(request: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """
    Exchange a valid refresh token for a new short-lived access token.
    The refresh token itself is NOT rotated (simpler for mobile — just retry on 401).
    """
    # Decode and type-check
    try:
        payload = _decode_token(request.refresh_token)
    except UnauthenticatedException as exc:
        raise BadRequestException(exc.message)

    if payload.get("type") != "refresh":
        raise BadRequestException("A valid refresh token is required")

    user_id = str(payload.get("sub"))
    token_ver = payload.get("ver", 1)
    jti = payload.get("jti", "")

    # Load user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise BadRequestException("User not found")

    if getattr(user, "status", "active") == "hold":
        raise UnauthenticatedException("Account is on hold. Please contact support.")

    # Validate refresh_token_version (logout bumps this)
    if token_ver != (user.refresh_token_version or 1):
        raise UnauthenticatedException("Refresh token has been revoked. Please log in again.")

    # Validate the JTI hash matches what we stored (single-device refresh token binding)
    if not user.refresh_token_hash or not secrets.compare_digest(
        hash_refresh_jti(jti), user.refresh_token_hash
    ):
        raise UnauthenticatedException("Refresh token is invalid. Please log in again.")

    # Issue a new access token
    new_access = create_access_token(user.id, token_version=user.token_version)
    return RefreshResponse(access_token=new_access, token_type="bearer")


# ─── Logout ────────────────────────────────────────────────

@router.post("/logout", status_code=204)
async def logout(
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id_verified),
):
    """
    Invalidate the current session immediately.
    Bumps both token_version and refresh_token_version so neither the
    access token nor the refresh token can be used again.
    Clears the stored refresh token hash.
    """
    result = await db.execute(select(User).where(User.id == current_user_id))
    user = result.scalars().first()
    if not user:
        raise NotFoundException("User not found")

    user.token_version = (user.token_version or 1) + 1
    user.refresh_token_version = (user.refresh_token_version or 1) + 1
    user.refresh_token_hash = None
    await db.commit()
    # 204 No Content — no response body


# ─── Profile ───────────────────────────────────────────────

@router.patch("/profile", response_model=UserResponse)
async def update_profile(
    request: UpdateProfileRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id_verified),
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
        if request.avatar is not None:
            user.avatar = request.avatar
            user.has_chosen_avatar = True
        if request.gender is not None:
            user.gender = request.gender
            user.has_chosen_avatar = True
        if getattr(request, "roll_number", None) is not None:
            if not (len(request.roll_number) == 3 and request.roll_number.isdigit()):
                raise BadRequestException("College ID must be a 3-digit number (e.g. 101)")
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

    result = await db.execute(select(User).where(User.id == current_user_id))
    updated_user = result.scalars().first()
    return UserResponse.model_validate(updated_user)


@router.get("/me", response_model=UserResponse)
@router.get("/profile", response_model=UserResponse)
async def get_current_user_profile(
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id_verified),
):
    """Retrieve full profile of the currently authenticated user."""
    result = await db.execute(select(User).where(User.id == current_user_id))
    user = result.scalars().first()
    if not user:
        raise NotFoundException("User not found")
    return UserResponse.model_validate(user)


# ─── Delete Account ────────────────────────────────────────

@router.delete("/account", response_model=DeleteAccountResponse, status_code=200)
async def delete_account(
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id_verified),
):
    """
    Request account deletion: marks user account status as 'hold' and
    immediately revokes all active session and refresh tokens.
    """
    result = await db.execute(select(User).where(User.id == current_user_id))
    user = result.scalars().first()
    if not user:
        raise NotFoundException("User not found")

    user.status = "hold"
    user.token_version = (user.token_version or 1) + 1
    user.refresh_token_version = (user.refresh_token_version or 1) + 1
    user.refresh_token_hash = None
    await db.commit()

    return DeleteAccountResponse(
        message="Account has been placed on hold.",
        status="hold",
    )


# ─── Forgot / Reset Password ───────────────────────────────

@router.post("/forgot-password", response_model=ForgotPasswordOtpResponse)
@router.post("/forget-password", response_model=ForgotPasswordOtpResponse, include_in_schema=False)
async def forgot_password(
    request: ForgotPasswordRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Initiate password reset: accepts email or phone number,
    looks up account, and sends a 6-digit OTP to user's registered email address.
    """
    client_ip = get_client_ip(http_request)
    await rate_limit_login(client_ip)

    identifier = request.identifier or request.email or request.phone or ""
    user = await find_user_by_identifier(db, identifier)
    if not user:
        raise NotFoundException("No account found with this email or phone number")

    if getattr(user, "status", "active") == "hold":
        raise BadRequestException("This account is currently on hold. Please contact support.")

    if not user.email:
        raise BadRequestException("No email address registered for this account. Please contact support.")

    sent, message, fallback_otp = await create_and_send_reset_otp(user, db)

    return ForgotPasswordOtpResponse(
        message=message,
        expires_in_minutes=settings.OTP_EXPIRY_MINUTES,
        masked_email=mask_email(user.email) if user.email else None,
        masked_phone=mask_phone(user.phone) if user.phone else None,
        delivery_failed=not sent,
        otp_failed=not sent,
        otp_sent=sent,
        status="otp_sent" if sent else "otp_failed",
        fallback_otp=fallback_otp,
    )


@router.post("/forgot-password/verify", response_model=VerifyResetOtpResponse)
@router.post("/forget-password/verify", response_model=VerifyResetOtpResponse, include_in_schema=False)
@router.post("/verify-reset-otp", response_model=VerifyResetOtpResponse, include_in_schema=False)
async def verify_reset_otp(
    request: VerifyResetOtpRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Verifies the password reset OTP sent to the user's phone number.
    Returns a secure reset_token valid for 15 minutes to proceed with changing the password.
    """
    client_ip = get_client_ip(http_request)
    await rate_limit_login(client_ip)

    identifier = request.identifier or request.email or request.phone or ""
    user = await find_user_by_identifier(db, identifier)
    if not user:
        raise NotFoundException("No account found with this email or phone number")

    if getattr(user, "status", "active") == "hold":
        raise BadRequestException("This account is currently on hold. Please contact support.")

    verification = (await db.execute(
        select(PasswordResetOtp).where(PasswordResetOtp.user_id == user.id)
    )).scalar_one_or_none()

    now = datetime.datetime.utcnow()
    if not verification or verification.expires_at <= now:
        raise BadRequestException("Verification code has expired. Please request a new code.")
    if verification.attempts >= settings.OTP_MAX_ATTEMPTS:
        raise BadRequestException("Too many invalid attempts. Please request a new code.")

    if not secrets.compare_digest(verification.code_hash, otp_hash(request.otp.strip())):
        verification.attempts += 1
        await db.commit()
        raise BadRequestException("Invalid verification code")

    # Generate short-lived reset token
    reset_token = create_password_reset_token(user.id, token_version=user.token_version or 1)
    verification.reset_token_hash = hashlib.sha256(reset_token.encode("utf-8")).hexdigest()
    await db.commit()

    return VerifyResetOtpResponse(
        message="OTP verified successfully. You can now reset your password.",
        reset_token=reset_token,
        status="verified",
    )


@router.post("/reset-password", response_model=ResetPasswordResponse)
@router.post("/forgot-password/reset", response_model=ResetPasswordResponse, include_in_schema=False)
@router.post("/forget-password/reset", response_model=ResetPasswordResponse, include_in_schema=False)
async def reset_password(
    request: ResetPasswordRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Resets the user's password using either the reset_token (from verification)
    or directly with identifier + otp.
    Invalidates all existing active sessions and refresh tokens across devices.
    """
    client_ip = get_client_ip(http_request)
    await rate_limit_login(client_ip)

    user = None
    verification = None

    if request.reset_token:
        try:
            payload = verify_password_reset_token(request.reset_token)
        except UnauthenticatedException as exc:
            raise BadRequestException(exc.message)

        user_id = str(payload.get("sub"))
        user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
        if not user:
            raise NotFoundException("User not found")

        token_hash = hashlib.sha256(request.reset_token.encode("utf-8")).hexdigest()
        verification = (await db.execute(
            select(PasswordResetOtp).where(
                PasswordResetOtp.user_id == user.id,
                PasswordResetOtp.reset_token_hash == token_hash,
            )
        )).scalar_one_or_none()
        if not verification:
            raise BadRequestException("Reset token is invalid or has already been used. Please request a new code.")
    else:
        identifier = request.identifier or request.email or request.phone or ""
        user = await find_user_by_identifier(db, identifier)
        if not user:
            raise NotFoundException("No account found with this email or phone number")

        verification = (await db.execute(
            select(PasswordResetOtp).where(PasswordResetOtp.user_id == user.id)
        )).scalar_one_or_none()

        now = datetime.datetime.utcnow()
        if not verification or verification.expires_at <= now:
            raise BadRequestException("Verification code has expired. Please request a new code.")
        if verification.attempts >= settings.OTP_MAX_ATTEMPTS:
            raise BadRequestException("Too many invalid attempts. Please request a new code.")

        if not secrets.compare_digest(verification.code_hash, otp_hash(request.otp)):
            verification.attempts += 1
            await db.commit()
            raise BadRequestException("Invalid verification code")

    if getattr(user, "status", "active") == "hold":
        raise BadRequestException("This account is currently on hold. Please contact support.")

    # Update password and revoke all existing sessions
    user.hashed_password = hash_password(request.new_password)
    user.token_version = (user.token_version or 1) + 1
    user.refresh_token_version = (user.refresh_token_version or 1) + 1
    user.refresh_token_hash = None

    if verification:
        await db.delete(verification)

    await db.commit()

    return ResetPasswordResponse(
        message="Password has been reset successfully. Please log in with your new password.",
        success=True,
    )


# ─────────────────────────────────────────────
# FCM Device Token Management
# ─────────────────────────────────────────────

async def record_user_device_token(
    db: AsyncSession,
    user_id: str,
    fcm_token: str,
    device_name: Optional[str] = "Android Device",
    platform: Optional[str] = "android",
) -> None:
    """
    Registers or updates an FCM token in PostgreSQL and Cloud Firestore.
    """
    token = (fcm_token or "").strip()
    if not token:
        return

    # 1. Store in PostgreSQL
    stmt = pg_insert(UserFcmToken).values(
        user_id=user_id,
        fcm_token=token,
        device_name=device_name or "Android Device",
        platform=platform or "android"
    ).on_conflict_do_update(
        index_elements=["fcm_token"],
        set_={
            "user_id": user_id,
            "device_name": device_name or "Android Device",
            "platform": platform or "android",
            "updated_at": datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        }
    )
    await db.execute(stmt)
    await db.commit()

    # 2. Store in Cloud Firestore (MongoDB mode or Native mode)
    try:
        from app.services.firestore_sync import sync_token_to_firestore
        await sync_token_to_firestore(
            user_id=user_id,
            token=token,
            device_name=device_name or "Android Device",
            platform=platform or "android"
        )
    except Exception as e:
        logger.warning(f"[Firestore] Failed to sync token to Firestore: {e}")


@router.post("/device-token", response_model=DeviceTokenResponse, status_code=status.HTTP_200_OK)
async def register_device_token(
    request: DeviceTokenRequest,
    user_id: str = Depends(get_current_user_id_verified),
    db: AsyncSession = Depends(get_db)
):
    """
    Register or update an FCM device token for the authenticated user.
    Uses PostgreSQL ON CONFLICT (UPSERT) to ensure one active owner per token.
    """
    token = (request.fcm_token or "").strip()
    if not token:
        raise BadRequestException("fcmToken cannot be empty")

    await record_user_device_token(
        db=db,
        user_id=user_id,
        fcm_token=token,
        device_name=request.device_name,
        platform=request.platform,
    )

    return DeviceTokenResponse(success=True, message="FCM device token registered in PostgreSQL and Firestore")


@router.delete("/device-token", response_model=DeviceTokenResponse, status_code=status.HTTP_200_OK)
async def unregister_device_token(
    request: DeviceTokenRequest,
    user_id: Optional[str] = Depends(get_current_user_id_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Remove an FCM device token upon user logout from both PostgreSQL and Firestore.
    Safe to call with or without an active session (e.g. during logout or when access token expired).
    """
    token = (request.fcm_token or "").strip()
    if token:
        # 1. Delete from PostgreSQL
        if user_id:
            query = select(UserFcmToken).where(
                UserFcmToken.fcm_token == token,
                UserFcmToken.user_id == user_id
            )
        else:
            query = select(UserFcmToken).where(
                UserFcmToken.fcm_token == token
            )
        result = await db.execute(query)
        records = result.scalars().all()
        for record in records:
            await db.delete(record)
        if records:
            await db.commit()

        # 2. Delete from Cloud Firestore
        try:
            from app.services.firestore_sync import remove_token_from_firestore
            await remove_token_from_firestore(user_id=user_id, token=token)
        except Exception as e:
            logger.warning(f"[Firestore] Failed to remove token from Firestore: {e}")

    return DeviceTokenResponse(success=True, message="Device token removed successfully from PostgreSQL and Firestore")


