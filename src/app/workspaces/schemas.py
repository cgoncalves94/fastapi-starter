"""
Workspace Pydantic schemas.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import EmailStr, Field, field_validator

from app.core.common import BaseSchema, TimestampMixin
from app.workspaces.models import WorkspaceRole


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


# Clean minimal schemas for member operations
class WorkspaceMemberCreate(BaseSchema):
    """Schema for adding a member to workspace."""

    user_id: UUID
    role: WorkspaceRole = WorkspaceRole.MEMBER


class WorkspaceMemberUpdate(BaseSchema):
    """Schema for updating workspace member."""

    role: WorkspaceRole


# Minimal user info for member display
class MemberUser(BaseSchema):
    """Minimal user info for workspace members."""

    id: UUID
    firstname: str | None = None
    lastname: str | None = None
    email: EmailStr


# Minimal member info for display
class WorkspaceMember(BaseSchema):
    """Clean workspace member info."""

    role: WorkspaceRole
    joined_at: datetime
    user: MemberUser


# Clean workspace response
class WorkspaceInfo(BaseSchema):
    """Clean workspace info without timestamps."""

    id: UUID
    name: str
    slug: str
    description: str | None = None
    member_count: int = 0


class WorkspaceWithMemberDetails(WorkspaceInfo):
    """Workspace with clean member details."""

    members: list[WorkspaceMember] = Field(default_factory=list)
