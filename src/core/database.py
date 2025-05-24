"""
Database configuration and session management (Async).
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.core.config import get_settings

settings = get_settings()

# Create async engine
async_engine = create_async_engine(
    settings.async_database_url,
    echo=settings.database_echo,
)

# Async session factory
AsyncSessionFactory = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)
