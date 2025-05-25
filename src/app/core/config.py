"""
Application configuration using Pydantic Settings.
"""

import os
from functools import lru_cache
from logging.config import dictConfig

from dotenv import load_dotenv
from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = os.getenv("APP_NAME", "FastAPI Starter")
    app_version: str = os.getenv("APP_VERSION", "0.1.0")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Database
    database_echo: bool = os.getenv("DATABASE_ECHO", "false").lower() == "true"

    # PostgreSQL components (for building DATABASE_URL)
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    postgres_user: str = os.getenv("POSTGRES_USER", "postgres")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    postgres_db: str = os.getenv("POSTGRES_DB", "fastapi_starter")

    @property
    def database_url(self) -> str:
        """Build database URL from PostgreSQL components."""
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

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

    # Initial Superuser
    first_superuser: EmailStr = os.getenv("FIRST_SUPERUSER", "admin@example.com")
    first_superuser_password: str = os.getenv("FIRST_SUPERUSER_PASSWORD", "changethis")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


def setup_logging() -> None:
    """
    Configures logging for the application using dictConfig for flexibility.
    Uses Uvicorn's default loggers and formatters for consistency.
    """
    settings = get_settings()
    log_level = "INFO" if settings.debug else "WARNING"

    # Default Uvicorn logging configuration
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(asctime)s - %(levelprefix)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "use_colors": True,
            },
            "access": {
                "()": "uvicorn.logging.AccessFormatter",
                "fmt": '%(asctime)s - %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "use_colors": True,
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["default"],
                "level": log_level,
                "propagate": False,
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["default"],
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["access"],
                "level": "INFO",
                "propagate": False,
            },
            "": {"handlers": ["default"], "level": log_level, "propagate": False},
        },
    }

    dictConfig(LOGGING_CONFIG)
