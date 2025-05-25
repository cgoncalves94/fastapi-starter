"""
User repository with specific user operations.
"""

from uuid import UUID

from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.base import BaseRepository
from app.users.models import User
from app.workspaces.models import Workspace, WorkspaceMember


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

    async def get_user_with_workspaces(
        self, user_id: UUID
    ) -> tuple[User | None, list[tuple[WorkspaceMember, Workspace]]]:
        """Get user with their workspace memberships using JOIN - User-centric query."""
        # Get user first
        user_statement = select(self.model).where(self.model.id == user_id)
        user_result = await self.session.execute(user_statement)
        user = user_result.scalar_one_or_none()

        # Get user's workspace memberships
        memberships = []
        if user:
            membership_statement = (
                select(WorkspaceMember, Workspace)
                .join(Workspace, WorkspaceMember.workspace_id == Workspace.id)
                .where(WorkspaceMember.user_id == user_id)
                .where(Workspace.is_active.is_(True))
            )
            membership_result = await self.session.execute(membership_statement)
            memberships = [
                (member, workspace) for member, workspace in membership_result.all()
            ]

        return user, memberships

    async def get_user_workspace_ids(self, user_id: UUID) -> list[UUID]:
        """Get lightweight list of workspace IDs for a user - fast lookup."""
        statement = (
            select(WorkspaceMember.workspace_id)
            .join(Workspace, WorkspaceMember.workspace_id == Workspace.id)
            .where(WorkspaceMember.user_id == user_id)
            .where(Workspace.is_active.is_(True))
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())
