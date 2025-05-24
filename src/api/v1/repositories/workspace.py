"""
Workspace repository with specific workspace operations.
"""

from uuid import UUID

from sqlmodel import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.models.workspace import Workspace
from src.api.v1.models.workspace_member import WorkspaceMember, WorkspaceRole
from src.api.v1.repositories.base import BaseRepository


# noinspection PyTypeChecker,PydanticTypeChecker
class WorkspaceRepository(BaseRepository[Workspace]):
    """Workspace repository."""

    def __init__(self, session: AsyncSession):
        super().__init__(Workspace, session)

    async def get_by_slug(self, slug: str) -> Workspace | None:
        """Get workspace by slug."""
        statement = select(self.model).where(self.model.slug == slug)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def is_slug_taken(self, slug: str, exclude_id: UUID | None = None) -> bool:
        """Check if slug is already taken."""
        statement = select(self.model).where(self.model.slug == slug)
        if exclude_id:
            statement = statement.where(self.model.id != exclude_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none() is not None

    async def get_user_workspaces(self, user_id: UUID) -> list[Workspace]:
        """Get all workspaces for a user."""
        statement = (
            select(self.model)
            .join(WorkspaceMember)
            .where(WorkspaceMember.user_id == user_id)
            .where(self.model.is_active.is_(True))
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_user_workspaces_paginated(
        self, user_id: UUID, skip: int = 0, limit: int = 20
    ) -> list[Workspace]:
        """Get paginated workspaces for a user."""
        statement = (
            select(self.model)
            .join(WorkspaceMember)
            .where(WorkspaceMember.user_id == user_id)
            .where(self.model.is_active.is_(True))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def count_user_workspaces(self, user_id: UUID) -> int:
        """Count total workspaces for a user."""
        statement = (
            select(func.count())
            .select_from(self.model)
            .join(WorkspaceMember)
            .where(WorkspaceMember.user_id == user_id)
            .where(self.model.is_active.is_(True))
        )
        result = await self.session.execute(statement)
        scalar_result = result.scalar_one_or_none()
        return scalar_result if scalar_result is not None else 0

    async def get_workspace_members(self, workspace_id: UUID) -> list[WorkspaceMember]:
        """Get all members of a workspace."""
        statement = select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def add_member(
        self,
        workspace_id: UUID,
        user_id: UUID,
        role: WorkspaceRole = WorkspaceRole.MEMBER,
        added_by_id: UUID | None = None,
    ) -> WorkspaceMember:
        """Add a member to workspace."""
        member_data = {
            "workspace_id": workspace_id,
            "user_id": user_id,
            "role": role,
            "added_by_id": added_by_id,
        }
        member = WorkspaceMember.model_validate(member_data)
        self.session.add(member)
        await self.session.flush()
        await self.session.refresh(member)
        return member

    async def remove_member(self, workspace_id: UUID, user_id: UUID) -> bool:
        """Remove a member from workspace."""
        statement = select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
        result = await self.session.execute(statement)
        member = result.scalar_one_or_none()
        if member:
            await self.session.delete(member)
            await self.session.flush()
            return True
        return False

    async def update_member_role(
        self, workspace_id: UUID, user_id: UUID, role: WorkspaceRole
    ) -> WorkspaceMember | None:
        """Update member role in workspace."""
        statement = select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
        result = await self.session.execute(statement)
        member = result.scalar_one_or_none()
        if member:
            update_data = {"role": role}
            # member.sqlmodel_update is correct here
            member.sqlmodel_update(update_data)
            self.session.add(member)
            await self.session.flush()
            await self.session.refresh(member)
            return member
        return None

    async def get_member(
        self, workspace_id: UUID, user_id: UUID
    ) -> WorkspaceMember | None:
        """Get specific workspace member."""
        statement = select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def is_user_member(self, workspace_id: UUID, user_id: UUID) -> bool:
        """Check if user is a member of workspace."""
        member = await self.get_member(workspace_id, user_id)
        return member is not None

    async def get_user_role_in_workspace(
        self, workspace_id: UUID, user_id: UUID
    ) -> WorkspaceRole | None:
        """Get user's role in workspace."""
        member = await self.get_member(workspace_id, user_id)
        return member.role if member else None
