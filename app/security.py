import hashlib
import secrets
from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import datetime
from typing import Optional
import bcrypt
from app.config import settings


# ─── Password Utilities ─────────────────────────────────────

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


async def verify_password_async(plain_password: str, hashed_password: str) -> bool:
    """Verifies password off the main asyncio thread to prevent blocking the event loop."""
    import asyncio
    return await asyncio.to_thread(verify_password, plain_password, hashed_password)


async def hash_password_async(password: str) -> str:
    """Hashes password off the main asyncio thread."""
    import asyncio
    return await asyncio.to_thread(hash_password, password)


# ─── Exceptions ─────────────────────────────────────────────

class UnauthenticatedException(Exception):
    """Custom exception raised for authorization or JWT validation failures."""
    def __init__(self, message: str):
        self.message = message


# ─── Token Creation ─────────────────────────────────────────

def create_access_token(
    user_id: str,
    role: str = "customer",
    canteen_id: str | None = None,
    token_version: int = 1,
) -> str:
    """
    Short-lived access token (default 15 minutes).
    Embedded 'type': 'access' prevents refresh tokens being used here.
    token_version is embedded so that when the user logs out, the old
    access token's version won't match the DB and will be rejected.
    """
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": user_id,
        "role": role,
        "ver": token_version,
        "type": "access",
        "iss": settings.JWT_ISSUER,
        "exp": expire,
    }
    if canteen_id:
        payload["canteen_id"] = str(canteen_id)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def create_refresh_token(user_id: str, refresh_version: int = 1) -> tuple[str, str]:
    """
    Long-lived refresh token (default 30 days).
    Returns (token_string, jti) — jti is the unique token ID that gets stored
    (hashed) in the DB so individual refresh tokens can be invalidated.
    """
    jti = secrets.token_urlsafe(32)  # cryptographically random, unique per token
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {
        "sub": user_id,
        "jti": jti,
        "ver": refresh_version,
        "type": "refresh",
        "iss": settings.JWT_ISSUER,
        "exp": expire,
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    return token, jti


def hash_refresh_jti(jti: str) -> str:
    """SHA-256 of the refresh token's JTI — stored in DB, never the raw JTI."""
    return hashlib.sha256(jti.encode("utf-8")).hexdigest()


# ─── Token Decoding ─────────────────────────────────────────

security_scheme = HTTPBearer(auto_error=False)


def _decode_token(token: str) -> dict:
    """Decode and validate JWT signature/expiry/issuer. Returns payload dict."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=["HS256"],
            issuer=settings.JWT_ISSUER,
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


# ─── Access-Token Dependencies ───────────────────────────────

async def get_current_user_id_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> Optional[str]:
    """
    Returns user_id if valid Bearer access token is provided, or None if missing.
    Useful for endpoints that customize results for logged-in users while remaining
    accessible to unauthenticated requests.
    """
    if not credentials or not credentials.credentials:
        return None
    try:
        payload = _decode_token(credentials.credentials)
        if payload.get("type") == "access":
            return str(payload.get("sub"))
    except Exception:
        pass
    return None


async def get_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> str:
    """
    Validates the access JWT and returns user_id.
    Does NOT check token_version — use get_current_user_id_verified for
    endpoints that need single-device / post-logout enforcement.
    """
    if not credentials:
        raise UnauthenticatedException("Authorization header is missing or empty")
    payload = _decode_token(credentials.credentials)
    if payload.get("type") != "access":
        raise UnauthenticatedException("A valid access token is required")
    return str(payload.get("sub"))


async def get_current_user_id_verified(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> str:
    """
    Validates the access JWT AND checks token_version against DB.
    If user logged out or logged in on a new device, this rejects the old
    token immediately.  Use this on all sensitive endpoints (orders, cart,
    profile, stream ticket).
    """
    if not credentials:
        raise UnauthenticatedException("Authorization header is missing or empty")
    payload = _decode_token(credentials.credentials)
    if payload.get("type") != "access":
        raise UnauthenticatedException("A valid access token is required")

    user_id = str(payload.get("sub"))
    token_ver = payload.get("ver", 1)

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
                "Session expired. Please log in again."
            )

    return user_id


# ─── Vendor Token Dependency ─────────────────────────────────

async def get_current_vendor(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
):
    """
    Validates access JWT and enforces vendor role (staff or admin).
    """
    if not credentials:
        raise UnauthenticatedException("Authorization header is missing or empty")
    payload = _decode_token(credentials.credentials)
    if payload.get("type") != "access":
        raise UnauthenticatedException("A valid access token is required")
    if payload.get("role") not in {"staff", "admin"}:
        raise UnauthenticatedException("Vendor access is required")
    return {
        "id": str(payload.get("sub")),
        "role": payload.get("role"),
        "canteen_id": payload.get("canteen_id"),
    }


# ─── App-Client Identity Guard ───────────────────────────────

async def require_app_client(request: Request) -> None:
    """
    Global dependency — applied to every route via FastAPI(dependencies=[...]).

    Rejects any request that does not carry the correct X-App-Key header.
    This stops casual browser, curl, and Postman access.

    When APP_CLIENT_KEY is None (development default) the check is skipped
    so local dev workflow is not disrupted.
    """
    if not settings.APP_CLIENT_KEY:
        # Guard disabled — development mode
        return
    header_value = request.headers.get(settings.APP_CLIENT_KEY_HEADER) or ""
    if not secrets.compare_digest(header_value, settings.APP_CLIENT_KEY):
        raise UnauthenticatedException(
            "Missing or invalid app client key. This API is only accessible from the official app."
        )


# ─── Helpers ─────────────────────────────────────────────────

def get_client_ip(request: Request) -> str:
    """
    Return the real client IP address.

    Behind a trusted reverse proxy (ngrok, Nginx, Caddy) the original client
    IP is forwarded in the X-Forwarded-For header. We only trust that header
    when the request arrives from a known proxy IP (settings.TRUSTED_PROXY_IPS).
    In all other cases we fall back to the raw socket peer address.
    """
    peer = request.client.host if request.client else "unknown"
    if peer in settings.TRUSTED_PROXY_IPS:
        forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        if forwarded:
            return forwarded
    return peer
