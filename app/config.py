import logging
import warnings
from pydantic_settings import BaseSettings

_config_logger = logging.getLogger("onfood.config")

_INSECURE_JWT_DEFAULT = "super_secret_key_for_development_purposes"


class Settings(BaseSettings):
    # ── Deployment mode ──────────────────────────────────────────────────────
    # Set to "production" in .env when running publicly. Controls security
    # header emission, log verbosity, and insecure-secret warnings.
    ENVIRONMENT: str = "development"

    # ── Database ─────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/onfood"
    SQL_ECHO: bool = False

    # ── JWT ──────────────────────────────────────────────────────────────────
    # IMPORTANT: rotate JWT_SECRET to a strong random value before any public
    # deployment. Generate one with:
    #   python -c "import secrets; print(secrets.token_hex(32))"
    JWT_SECRET: str = _INSECURE_JWT_DEFAULT
    JWT_ISSUER: str = "onfood"

    # ── Token lifetimes ───────────────────────────────────────────────────────
    # Short-lived access token (Bearer on every API call).
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    # Long-lived refresh token (sent ONLY to POST /api/auth/refresh).
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ── App-client identity guard ─────────────────────────────────────────────
    # Set APP_CLIENT_KEY to a strong random secret in .env.
    # Every request must carry this value in the APP_CLIENT_KEY_HEADER header.
    # Requests missing it receive 401 before any route logic runs.
    # Leave blank/None to disable the guard (development default).
    # Generate: python -c "import secrets; print(secrets.token_hex(32))"
    APP_CLIENT_KEY: str | None = None
    APP_CLIENT_KEY_HEADER: str = "X-App-Key"

    # ── OTP ──────────────────────────────────────────────────────────────────
    OTP_EXPIRY_MINUTES: int = 5
    OTP_MAX_ATTEMPTS: int = 5
    # Set separately from JWT_SECRET so that rotating one does not affect the other.
    OTP_HASH_SECRET: str | None = None

    # ── Redis / Cache ─────────────────────────────────────────────────────────
    CACHE_REDIS_URL: str | None = None
    MENU_CACHE_TTL_SECONDS: int = 120

    # ── Business rules ────────────────────────────────────────────────────────
    ORDER_COOLDOWN_SECONDS: int = 10

    # ── WhatsApp bot ──────────────────────────────────────────────────────────
    WHATSAPP_BOT_URL: str = "http://127.0.0.1:3000"
    WHATSAPP_BOT_INTERNAL_KEY: str | None = None

    # ── CORS ──────────────────────────────────────────────────────────────────
    # Comma-separated list of allowed browser origins, e.g.:
    #   CORS_ALLOWED_ORIGINS=https://your-ngrok-domain.ngrok-free.app
    # Leave as ["*"] only for local development (credentials will be disabled).
    CORS_ALLOWED_ORIGINS: list[str] = ["*"]

    # ── Reverse proxy ─────────────────────────────────────────────────────────
    # IP addresses of trusted upstream proxies (e.g. ngrok agent on loopback).
    # X-Forwarded-For is only trusted when the request arrives from one of these.
    TRUSTED_PROXY_IPS: list[str] = ["127.0.0.1"]

    # ── Feature flags ─────────────────────────────────────────────────────────
    # Set to False to suppress vendor coupon/banner endpoints while the vendor
    # router is disabled.
    VENDOR_ENDPOINTS_ENABLED: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()


def _check_security_config() -> None:
    """Emit warnings for known-insecure configuration values at startup."""
    if settings.JWT_SECRET == _INSECURE_JWT_DEFAULT or len(settings.JWT_SECRET) < 32:
        msg = (
            "[SECURITY WARNING] JWT_SECRET is set to the insecure development default "
            "or is shorter than 32 characters. "
            "Rotate it before exposing this server publicly.\n"
            "  Generate a strong secret:  "
            "python -c \"import secrets; print(secrets.token_hex(32))\""
        )
        if settings.ENVIRONMENT == "production":
            # In production this is a hard error — the server should not run with a weak secret.
            raise RuntimeError(msg)
        warnings.warn(msg, stacklevel=2)
        _config_logger.warning(msg)

    if settings.OTP_HASH_SECRET is None:
        _config_logger.warning(
            "[SECURITY WARNING] OTP_HASH_SECRET is not set. "
            "OTPs will be hashed using JWT_SECRET as the fallback. "
            "Set a separate OTP_HASH_SECRET in .env."
        )


_check_security_config()

