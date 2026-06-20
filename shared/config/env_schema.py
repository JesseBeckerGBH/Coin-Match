"""Shared environment configuration for all CoinMatch services."""
import os
from dataclasses import dataclass, field

@dataclass
class Settings:
    app_env: str = field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    database_url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", ""))
    redis_url: str = field(default_factory=lambda: os.getenv("REDIS_URL", ""))
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    anthropic_api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    stripe_secret_key: str = field(default_factory=lambda: os.getenv("STRIPE_SECRET_KEY", ""))
    whop_api_key: str = field(default_factory=lambda: os.getenv("WHOP_API_KEY", ""))

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

def get_settings() -> Settings:
    return Settings()
