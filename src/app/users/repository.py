"""
User repository with specific user operations.
"""

from uuid import UUID

from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.base import BaseRepository
from app.users.models import User


class UserRepository(BaseRepository[User]):
    """User repository."""

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: EmailStr) -> User | None:
        """Get user by email."""
        statement = select(self.model).where(self.model.email == email)
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
