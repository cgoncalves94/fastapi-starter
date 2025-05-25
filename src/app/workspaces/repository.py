"""
Workspace repository with specific workspace operations.
"""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import func, select

from app.core.base import BaseRepository
from app.users.models import User
from app.workspaces.models import Workspace, WorkspaceMember, WorkspaceRole


class WorkspaceRepository(BaseRepository[Workspace]):
    """Workspace repository."""

    def __init__(self, session: AsyncSession):
        super().__init__(Workspace, session)

    # ========================================
    # WORKSPACE CRUD OPERATIONS
    # ========================================

    # READ
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

    async def get_user_workspaces_paginated(
        self, user_id: UUID, skip: int = 0, limit: int = 20
    ) -> Sequence[Workspace]:
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
        return result.scalars().all()

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

    # ========================================
    # WORKSPACE MEMBER CRUD OPERATIONS
    # ========================================

    # CREATE
    async def add_member(
        self,
        workspace_id: UUID,
        user_id: UUID,
        role: WorkspaceRole = WorkspaceRole.MEMBER,
        added_by_email: str | None = None,
    ) -> WorkspaceMember:
        """Add a member to workspace."""
        member_data = {
            "workspace_id": workspace_id,
            "user_id": user_id,
            "role": role,
            "added_by_email": added_by_email,
        }
        member = WorkspaceMember.model_validate(member_data)
        self.session.add(member)
        await self.session.flush()
        await self.session.refresh(member)
        return member

    # READ
    async def get_workspace_members(
        self, workspace_id: UUID
    ) -> Sequence[WorkspaceMember]:
        """Get all members of a workspace."""
        statement = select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_workspace_members_with_users(
        self, workspace_id: UUID
    ) -> Sequence[tuple[WorkspaceMember, User]]:
        """Get workspace members with their user details using JOIN."""
        statement = (
            select(WorkspaceMember, User)
            .join(User, WorkspaceMember.user_id == User.id)
            .where(WorkspaceMember.workspace_id == workspace_id)
            .where(User.is_active.is_(True))
        )
        result = await self.session.execute(statement)
        rows = result.all()
        return [(member, user) for member, user in rows]

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

    # UPDATE
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
            member.sqlmodel_update(update_data)
            self.session.add(member)
            await self.session.flush()
            await self.session.refresh(member)
            return member
        return None

    # DELETE
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
