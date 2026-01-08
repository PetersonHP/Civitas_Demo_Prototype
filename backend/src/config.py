from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Civitas Demo"
    debug: bool = False  # Changed to False for production

    # Database - Handle Heroku's DATABASE_URL
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://civitas_user:password@localhost:5432/civitas_db"
    )

    # CORS - Will be updated via environment variable
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"

    # Security
    secret_key: str = "change-this-in-production"

    # AI / LLM
    anthropic_api_key: str = ""
    groq_api_key: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Heroku uses postgres:// but SQLAlchemy needs postgresql://
        if self.database_url and self.database_url.startswith("postgres://"):
            self.database_url = self.database_url.replace("postgres://", "postgresql://", 1)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
