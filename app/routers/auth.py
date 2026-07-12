from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import User
from app.schemas import RegisterRequest, UserResponse, LoginRequest, LoginResponse, UpdateProfileRequest
from app.security import hash_password, verify_password, create_access_token, UnauthenticatedException, get_current_user_id
from app.exceptions import BadRequestException, NotFoundException
from app.security_rules import enforce_ip_account_limit

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=LoginResponse, status_code=201)
async def register(request: RegisterRequest, http_request: Request, db: AsyncSession = Depends(get_db)):
    """Registers a new user on the platform. Encrypts password using bcrypt."""
    async with db.begin():
        # Check if email is already registered
        result = await db.execute(select(User).where(User.email == request.email))
        existing_user = result.scalars().first()
        if existing_user:
            raise BadRequestException("A user with this email address already exists")

        client_ip = http_request.client.host if http_request.client else "unknown"
        await enforce_ip_account_limit(client_ip, request.email)

        # Create new User object and save to DB
        new_user = User(
            name=request.name,
            email=request.email,
            phone=request.phone,
            hashed_password=hash_password(request.password)
        )
        db.add(new_user)
        await db.flush()

    # Re-retrieve to return correctly
    result = await db.execute(select(User).where(User.id == new_user.id))
    saved_user = result.scalars().first()
    token = create_access_token(saved_user.id)
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(saved_user)
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

    client_ip = http_request.client.host if http_request.client else "unknown"
    await enforce_ip_account_limit(client_ip, request.email)

    # Generate token
    token = create_access_token(user.id)
    
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
        if request.password is not None:
            user.hashed_password = hash_password(request.password)
            
        await db.flush()
        
    # Re-retrieve to return updated state
    result = await db.execute(select(User).where(User.id == current_user_id))
    updated_user = result.scalars().first()
    return UserResponse.model_validate(updated_user)
