from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import datetime
from typing import Optional
import bcrypt
from app.config import settings

def hash_password(password: str) -> str:
    """Hashes a plain text password using bcrypt."""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain text password against its hashed value."""
    try:
        pwd_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    except Exception:
        return False

def create_access_token(user_id: str, role: str = "customer", canteen_id: str | None = None, token_version: int = 1) -> str:
    """
    Generates a signed, stateless JWT access token.
    token_version is embedded so that when the user logs in on a new device,
    the old token's version won't match the DB and will be rejected.
    """
    payload = {
        "sub": user_id,
        "role": role,
        "ver": token_version,          # <── session version
        "iss": settings.JWT_ISSUER,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    }
    if canteen_id:
        payload["canteen_id"] = str(canteen_id)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


# Create HTTPBearer instance. auto_error=False allows us to raise custom exception
security_scheme = HTTPBearer(auto_error=False)

class UnauthenticatedException(Exception):
    """Custom exception raised for authorization or JWT validation failures."""
    def __init__(self, message: str):
        self.message = message


def _decode_token(token: str) -> dict:
    """Decode and validate JWT signature/expiry. Returns payload dict."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=["HS256"],
            issuer=settings.JWT_ISSUER
        )
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthenticatedException("Token is missing user identification claim (sub)")
        return payload
    except jwt.ExpiredSignatureError:
        raise UnauthenticatedException("Token has expired")
    except jwt.InvalidIssuerError:
        raise UnauthenticatedException("Invalid token issuer")
    except jwt.InvalidTokenError as e:
        raise UnauthenticatedException(f"Invalid authentication token: {str(e)}")


async def get_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)
) -> str:
    """
    Validates JWT and returns user_id.
    Does NOT check token_version — use get_current_user_id_verified for protected endpoints
    that need single-device enforcement.
    """
    if not credentials:
        raise UnauthenticatedException("Authorization header is missing or empty")
    payload = _decode_token(credentials.credentials)
    return str(payload.get("sub"))


async def get_current_user_id_verified(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)
) -> str:
    """
    Validates JWT AND checks token_version against DB.
    If user logged in on a new device, this rejects the old token immediately.
    Use this on sensitive endpoints (orders, cart, profile).
    """
    if not credentials:
        raise UnauthenticatedException("Authorization header is missing or empty")
    payload = _decode_token(credentials.credentials)
    user_id = str(payload.get("sub"))
    token_ver = payload.get("ver", 1)

    # Check version against DB
    from app.database import AsyncSessionLocal
    from sqlalchemy.future import select
    from app.models import User
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User.token_version).where(User.id == user_id))
        row = result.first()
        if row is None:
            raise UnauthenticatedException("User account not found")
        db_version = row[0] or 1
        if token_ver != db_version:
            raise UnauthenticatedException(
                "Session expired. You have logged in on another device. Please log in again."
            )

    return user_id


async def get_current_vendor(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)):
    if not credentials:
        raise UnauthenticatedException("Authorization header is missing or empty")
    try:
        payload = jwt.decode(credentials.credentials, settings.JWT_SECRET,
                             algorithms=["HS256"], issuer=settings.JWT_ISSUER)
        if payload.get("role") not in {"staff", "admin"}:
            raise UnauthenticatedException("Vendor access is required")
        return {"id": str(payload.get("sub")), "role": payload.get("role"), "canteen_id": payload.get("canteen_id")}
    except UnauthenticatedException:
        raise
    except jwt.ExpiredSignatureError:
        raise UnauthenticatedException("Token has expired")
    except jwt.InvalidTokenError as e:
        raise UnauthenticatedException(f"Invalid authentication token: {str(e)}")
