"""
Application configuration using Pydantic Settings.
"""

import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = os.getenv("APP_NAME", "FastAPI Starter")
    app_version: str = os.getenv("APP_VERSION", "0.1.0")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    # API
    api_v1_prefix: str = os.getenv("API_V1_PREFIX", "/api/v1")

    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")
    database_echo: bool = os.getenv("DATABASE_ECHO", "false").lower() == "true"

    # Security
    secret_key: str = os.getenv(
        "SECRET_KEY",
        "your-super-secret-key-change-in-production-make-it-long-and-random",
    )
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    # CORS
    cors_origins: list[str] = eval(
        os.getenv(
            "CORS_ORIGINS",
            '["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:3000", "http://127.0.0.1:8000"]',
        )
    )
    cors_allow_credentials: bool = (
        os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
    )
    cors_allow_methods: list[str] = eval(os.getenv("CORS_ALLOW_METHODS", '["*"]'))
    cors_allow_headers: list[str] = eval(os.getenv("CORS_ALLOW_HEADERS", '["*"]'))


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
