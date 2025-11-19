from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Civitas Demo"
    debug: bool = True

    # Database
    database_url: str = "postgresql://civitas_user:password@localhost:5432/civitas_db"

    # CORS
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"

    # Security
    secret_key: str = "change-this-in-production"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
