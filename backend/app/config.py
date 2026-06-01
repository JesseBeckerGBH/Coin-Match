"""Application configuration — loaded from environment variables."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_ENV: str = "development"
    APP_URL: str = "http://localhost:3000"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/coinmatch"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Auth
    JWT_SECRET: str = "change-me-in-production-min-32-chars"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 72

    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None

    # Stripe Connect
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_CONNECT_CLIENT_ID: Optional[str] = None

    # Claude Vision (AI coin grader)
    ANTHROPIC_API_KEY: Optional[str] = None
    CLAUDE_MODEL: str = "claude-sonnet-4-6"

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    # Owner
    OWNER_EMAIL: str = "jessebecker2021@gmail.com"

    # File uploads
    MAX_UPLOAD_SIZE_MB: int = 10
    UPLOAD_DIR: str = "static/uploads"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
