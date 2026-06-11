from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/p2psuperbot"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_EXPIRE_DAYS: int = 30

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "P2PSuperBot <noreply@example.com>"

    TELEGRAM_BOT_TOKEN: str = ""

    TRON_API_URL: str = "https://api.trongrid.io"
    BSC_RPC_URL: str = "https://bsc-dataseed.binance.org/"

    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # Rate limiting
    REGISTER_RATE_LIMIT: str = "5/hour"
    LOGIN_RATE_LIMIT: str = "10/minute"
    PASSWORD_RESET_RATE_LIMIT: str = "3/hour"

    # Security
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_MINUTES: int = 15
    TEMP_PASSWORD_EXPIRE_HOURS: int = 24

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
