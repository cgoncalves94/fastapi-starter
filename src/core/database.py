"""
Database configuration and session management (Async).
"""

from sqlmodel import SQLModel
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


async def init_db() -> None:
    """Initialize database tables (for async)."""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
