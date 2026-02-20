"""Configuration management using pydantic-settings."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Database
    database_url: str = "sqlite:///./bewerbungs_agent.db"

    # Gmail API
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_redirect_uri: str = "http://localhost:8080/oauth2callback"

    # OpenAI (optional)
    openai_api_key: Optional[str] = None

    # Stripe
    stripe_public_key: Optional[str] = None
    stripe_secret_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None

    # Application
    app_env: str = "development"
    log_level: str = "INFO"
    secret_key: str = "change_this_in_production"

    # Multi-tenant Limits
    max_applications_free: int = 10
    max_applications_pro: int = 100
    max_applications_agency: int = 999999  # "unlimited"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
