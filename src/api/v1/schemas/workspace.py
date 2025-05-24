"""
Workspace Pydantic schemas.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import Field, field_validator

from src.api.v1.models.workspace_member import WorkspaceRole
from src.api.v1.schemas.common import BaseSchema, TimestampMixin
from src.api.v1.schemas.shared import BasicUserInfo


class WorkspaceBase(BaseSchema):
    """Base workspace schema."""

    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    is_active: bool = True

    @classmethod
    @field_validator("slug")
    def validate_slug(cls, v: str) -> str:
        """Validate slug format."""
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError(
                "Slug must contain only letters, numbers, hyphens, and underscores"
            )
        return v.lower()


class WorkspaceCreate(WorkspaceBase):
    """Schema for creating a workspace."""

    pass


class WorkspaceUpdate(BaseSchema):
    """Schema for updating a workspace."""

    name: str | None = Field(None, min_length=1, max_length=100)
    slug: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    is_active: bool | None = None


class WorkspaceResponse(WorkspaceBase, TimestampMixin):
    """Schema for workspace response."""

    id: UUID


class WorkspaceMemberBase(BaseSchema):
    """Base workspace member schema."""

    user_id: UUID
    workspace_id: UUID
    role: WorkspaceRole = WorkspaceRole.MEMBER


class WorkspaceMemberCreate(BaseSchema):
    """Schema for adding a member to workspace."""

    user_id: UUID
    role: WorkspaceRole = WorkspaceRole.MEMBER


class WorkspaceMemberUpdate(BaseSchema):
    """Schema for updating workspace member."""

    role: WorkspaceRole


class WorkspaceMemberResponse(WorkspaceMemberBase):
    """Schema for workspace member response."""

    id: UUID
    joined_at: datetime
    added_by_id: UUID | None = None


class WorkspaceMemberWithUser(WorkspaceMemberResponse):
    """Workspace member with user information."""

    user: BasicUserInfo


class WorkspaceWithMembers(WorkspaceResponse):
    """Workspace with members information."""

    members: list[WorkspaceMemberWithUser] = []
    member_count: int = 0


class WorkspaceMembershipResponse(BaseSchema):
    """User's workspace membership details."""

    workspace: WorkspaceResponse
    role: WorkspaceRole
    joined_at: datetime
