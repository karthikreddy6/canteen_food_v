from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/onfood"
    SQL_ECHO: bool = False
    JWT_SECRET: str = "super_secret_key_for_development_purposes"
    JWT_ISSUER: str = "onfood"
    CACHE_REDIS_URL: str | None = None
    MENU_CACHE_TTL_SECONDS: int = 120
    ORDER_COOLDOWN_SECONDS: int = 10
    WHATSAPP_BOT_URL: str = "http://127.0.0.1:3000"
    WHATSAPP_BOT_INTERNAL_KEY: str | None = None
    OTP_EXPIRY_MINUTES: int = 5
    OTP_MAX_ATTEMPTS: int = 5
    OTP_HASH_SECRET: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
