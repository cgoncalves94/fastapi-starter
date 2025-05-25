"""
Database configuration and session management (Async).
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import select

from app.core.security import get_password_hash
from app.users.models import User

from .config import get_settings

settings = get_settings()

# Create async engine
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.database_echo,
)

# Async session factory
AsyncSessionFactory = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db() -> None:
    """Initialize database with first superuser if it doesn't exist."""
    async with AsyncSessionFactory() as session:
        result = await session.execute(
            select(User).where(User.email == settings.first_superuser)
        )
        existing_user = result.scalar_one_or_none()

        if not existing_user:
            user = User(
                email=settings.first_superuser,
                hashed_password=get_password_hash(settings.first_superuser_password),
                is_superuser=True,
                is_active=True,
            )
            session.add(user)
            await session.commit()
            logging.info(f"✅ Created superuser: {settings.first_superuser}")
