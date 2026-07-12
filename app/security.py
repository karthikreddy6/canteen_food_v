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

def create_access_token(user_id: str) -> str:
    """Generates a signed, stateless JWT access token for a user."""
    payload = {
        "sub": user_id,
        "iss": settings.JWT_ISSUER,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


# Create HTTPBearer instance. auto_error=False allows us to raise custom exception
security_scheme = HTTPBearer(auto_error=False)

class UnauthenticatedException(Exception):
    """Custom exception raised for authorization or JWT validation failures."""
    def __init__(self, message: str):
        self.message = message

async def get_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)
) -> str:
    if not credentials:
        raise UnauthenticatedException("Authorization header is missing or empty")
    
    token = credentials.credentials
    try:
        # Decode and verify signature, audience (if configured), and issuer
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=["HS256"],
            issuer=settings.JWT_ISSUER
        )
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthenticatedException("Token is missing user identification claim (sub)")
        return str(user_id)
    except jwt.ExpiredSignatureError:
        raise UnauthenticatedException("Token has expired")
    except jwt.InvalidIssuerError:
        raise UnauthenticatedException("Invalid token issuer")
    except jwt.InvalidTokenError as e:
        raise UnauthenticatedException(f"Invalid authentication token: {str(e)}")
