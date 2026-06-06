from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Steam API Configuration
    steam_api_key: str
    steam_id: str

    # Database Configuration
    database_url: str = "sqlite:///./cs2_tracker.db"

    # Application Settings
    update_interval_minutes: int = 60
    price_alert_threshold: float = 10.0

    # Price API
    price_api_url: str = "https://steamcommunity.com/market/priceoverview/"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
