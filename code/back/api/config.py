"""Application configuration using pydantic-settings.

Environment variables can be set in a .env file or passed directly.
"""

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database - individual components (from docker-compose)
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "coffee_user"
    POSTGRES_PASSWORD: str = "coffee_pass"
    POSTGRES_DB: str = "coffee_db"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        """Build async database URL from components."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # JWT Authentication
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Application
    DEBUG: bool = False
    API_TITLE: str = "Coffee Inventory Planning API"
    API_VERSION: str = "2.0.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
