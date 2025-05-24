"""
User repository with specific user operations.
"""

from uuid import UUID

from pydantic import EmailStr
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.models.user import User
from src.api.v1.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """User repository."""

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: EmailStr) -> User | None:
        """Get user by email."""
        statement = select(self.model).where(self.model.email == email)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """Get user by username."""
        statement = select(self.model).where(self.model.username == username)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_email_or_username(self, identifier: str) -> User | None:
        """Get user by email or username."""
        statement = select(self.model).where(
            (self.model.email == identifier) | (self.model.username == identifier)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def is_email_taken(
        self, email: EmailStr, exclude_id: UUID | None = None
    ) -> bool:
        """Check if email is already taken."""
        statement = select(self.model).where(self.model.email == email)
        if exclude_id:
            statement = statement.where(self.model.id != exclude_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none() is not None

    async def is_username_taken(
        self, username: str, exclude_id: UUID | None = None
    ) -> bool:
        """Check if username is already taken."""
        statement = select(self.model).where(self.model.username == username)
        if exclude_id:
            statement = statement.where(self.model.id != exclude_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none() is not None

    async def get_active_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get active users only."""
        statement = (
            select(self.model)
            .where(self.model.is_active.is_(True))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())
