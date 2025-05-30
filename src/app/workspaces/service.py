"""
Workspace service with business logic.
"""

import math
from uuid import UUID

from app.core.common import PaginatedResponse, PaginationParams
from app.core.exceptions import (
    ConflictError,
    NotFoundError,
    ValidationError,
)
from app.users.repository import UserRepository
from app.workspaces.models import WorkspaceRole
from app.workspaces.repository import WorkspaceRepository
from app.workspaces.schemas import (
    MemberUser,
    WorkspaceCreate,
    WorkspaceMember,
    WorkspaceMemberCreate,
    WorkspaceMemberUpdate,
    WorkspaceResponse,
    WorkspaceUpdate,
    WorkspaceWithMemberDetails,
)


class WorkspaceService:
    """Workspace service organized by CRUD operations."""

    def __init__(
        self, user_repository: UserRepository, workspace_repository: WorkspaceRepository
    ):
        self.user_repository = user_repository
        self.workspace_repository = workspace_repository

    # ========================================
    # WORKSPACE CRUD OPERATIONS
    # ========================================

    # CREATE
    async def create_workspace(
        self, workspace_data: WorkspaceCreate, owner_id: UUID
    ) -> WorkspaceResponse:
        """Create a new workspace."""
        # Check if slug is already taken
        if await self.workspace_repository.is_slug_taken(workspace_data.slug):
            raise ConflictError("Workspace slug already taken")

        # Create workspace data
        workspace_create_data = workspace_data.model_dump()

        # Create workspace
        workspace = await self.workspace_repository.create(obj_in=workspace_create_data)

        # Add creator as owner
        await self.workspace_repository.add_member(
            workspace_id=workspace.id,
            user_id=owner_id,
            role=WorkspaceRole.OWNER,
            added_by_email=None,
        )

        return WorkspaceResponse.model_validate(workspace)

    # READ
    async def get_workspace_by_id(self, workspace_id: UUID) -> WorkspaceResponse:
        """Get workspace by ID."""
        workspace = await self.workspace_repository.get_by_id(workspace_id)
        if not workspace:
            raise NotFoundError("Workspace not found")
        return WorkspaceResponse.model_validate(workspace)

    async def get_workspace_by_slug(self, slug: str) -> WorkspaceResponse:
        """Get workspace by slug."""
        workspace = await self.workspace_repository.get_by_slug(slug)
        if not workspace:
            raise NotFoundError(f"Workspace with slug '{slug}' not found")
        return WorkspaceResponse.model_validate(workspace)

    async def get_all_workspaces_paginated(
        self, pagination: PaginationParams
    ) -> PaginatedResponse[WorkspaceResponse]:
        """Get all workspaces with pagination (admin only)."""
        # Get workspaces with pagination
        workspaces = await self.workspace_repository.get_multi(
            skip=pagination.offset, limit=pagination.per_page
        )

        # Get total count
        total = await self.workspace_repository.count()

        # Calculate total pages (avoid division by zero)
        per_page = max(pagination.per_page, 1)
        pages = math.ceil(total / per_page) if total > 0 else 0

        # Convert to response models
        workspace_responses = [
            WorkspaceResponse.model_validate(workspace) for workspace in workspaces
        ]

        return PaginatedResponse[WorkspaceResponse](
            items=workspace_responses,
            total=total,
            page=pagination.page,
            per_page=pagination.per_page,
            pages=pages,
        )

    async def get_workspace_with_member_details(
        self, workspace_id: UUID
    ) -> WorkspaceWithMemberDetails:
        """Get workspace with clean member details using JOIN - efficient single query."""
        workspace = await self.workspace_repository.get_by_id(workspace_id)
        if not workspace:
            raise NotFoundError("Workspace not found")

        # Use JOIN query to get members with user details in one query
        members_with_users = (
            await self.workspace_repository.get_workspace_members_with_users(
                workspace_id
            )
        )

        # Convert to clean response format
        members = []
        for member, user in members_with_users:
            clean_member = WorkspaceMember(
                role=member.role,
                joined_at=member.joined_at,
                user=MemberUser(
                    id=user.id,
                    firstname=user.firstname,
                    lastname=user.lastname,
                    email=user.email,
                ),
            )
            members.append(clean_member)

        return WorkspaceWithMemberDetails(
            id=workspace.id,
            name=workspace.name,
            slug=workspace.slug,
            description=workspace.description,
            member_count=len(members),
            members=members,
        )

    # UPDATE
    async def update_workspace(
        self,
        workspace_id: UUID,
        workspace_data: WorkspaceUpdate,
    ) -> WorkspaceResponse:
        """Update workspace."""
        # Get existing workspace
        workspace = await self.workspace_repository.get_by_id(workspace_id)
        if not workspace:
            raise NotFoundError("Workspace not found")

        # Get only the fields that were actually provided
        update_data = workspace_data.model_dump(exclude_unset=True)

        # Handle slug uniqueness validation
        if "slug" in update_data and update_data["slug"] != workspace.slug:
            if await self.workspace_repository.is_slug_taken(
                update_data["slug"], exclude_id=workspace_id
            ):
                raise ConflictError("Workspace slug already taken")
            update_data["slug"] = update_data["slug"].lower()

        # Update workspace
        updated_workspace = await self.workspace_repository.update(
            db_obj=workspace, obj_in=update_data
        )
        return WorkspaceResponse.model_validate(updated_workspace)

    # DELETE
    async def delete_workspace(self, workspace_id: UUID) -> None:
        """Delete workspace (only owner)."""
        # First check if workspace exists
        workspace = await self.workspace_repository.get_by_id(workspace_id)
        if not workspace:
            raise NotFoundError("Workspace not found")

        # Delete all workspace members first (to avoid foreign key constraint issues)
        members = await self.workspace_repository.get_workspace_members(workspace_id)
        for member in members:
            await self.workspace_repository.remove_member(workspace_id, member.user_id)

        # Now delete the workspace
        await self.workspace_repository.delete(id=workspace_id)

    # ========================================
    # WORKSPACE MEMBER CRUD OPERATIONS
    # ========================================

    # CREATE
    async def add_member(
        self,
        workspace_id: UUID,
        member_data: WorkspaceMemberCreate,
        adder_id: UUID,
    ) -> WorkspaceResponse:
        """Add member to workspace."""
        # Check if workspace exists first
        workspace = await self.workspace_repository.get_by_id(workspace_id)
        if not workspace:
            raise NotFoundError("Workspace not found")

        # Check if user exists
        user = await self.user_repository.get_by_id(member_data.user_id)
        if not user:
            raise NotFoundError("User not found")

        # Check if user is already a member
        if await self.workspace_repository.is_user_member(
            workspace_id, member_data.user_id
        ):
            raise ConflictError("User is already a member of this workspace")

        # Add member
        adder_user = await self.user_repository.get_by_id(adder_id)
        await self.workspace_repository.add_member(
            workspace_id=workspace_id,
            user_id=member_data.user_id,
            role=member_data.role,
            added_by_email=adder_user.email if adder_user else None,
        )

        return WorkspaceResponse.model_validate(workspace)

    # UPDATE
    async def update_member_role(
        self,
        workspace_id: UUID,
        member_user_id: UUID,
        role_data: WorkspaceMemberUpdate,
        updater_id: UUID,
    ) -> WorkspaceResponse:
        """Update member role in workspace."""

        current_member_role = (
            await self.workspace_repository.get_user_role_in_workspace(
                workspace_id, member_user_id
            )
        )
        if (
            current_member_role == WorkspaceRole.OWNER
            and role_data.role != WorkspaceRole.OWNER
        ):
            raise ValidationError("Cannot change owner role")

        # Only owner can promote to admin (need to check if updater is owner)
        if role_data.role == WorkspaceRole.ADMIN:
            updater_role = await self.workspace_repository.get_user_role_in_workspace(
                workspace_id, updater_id
            )
            if updater_role != WorkspaceRole.OWNER:
                raise ValidationError("Only owner can promote members to admin")

        # Update member role
        await self.workspace_repository.update_member_role(
            workspace_id=workspace_id, user_id=member_user_id, role=role_data.role
        )

        workspace = await self.workspace_repository.get_by_id(workspace_id)
        if not workspace:
            raise NotFoundError("Workspace not found")
        return WorkspaceResponse.model_validate(workspace)

    # DELETE
    async def remove_member(self, workspace_id: UUID, member_user_id: UUID) -> None:
        """Remove member from workspace."""
        member_role = await self.workspace_repository.get_user_role_in_workspace(
            workspace_id, member_user_id
        )
        if member_role == WorkspaceRole.OWNER:
            raise ValidationError("Cannot remove workspace owner")

        # Remove member
        removed = await self.workspace_repository.remove_member(
            workspace_id, member_user_id
        )
        if not removed:
            raise NotFoundError("Member not found in workspace")
