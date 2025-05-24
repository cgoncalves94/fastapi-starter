"""
Shared schemas to avoid circular imports.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import EmailStr

from ..workspaces.models import WorkspaceRole
from .common import BaseSchema


class BasicUserInfo(BaseSchema):
    """Basic user information for cross-references."""

    id: UUID
    email: EmailStr
    username: str
    full_name: str | None = None
    is_active: bool = True


class BasicWorkspaceInfo(BaseSchema):
    """Basic workspace information for cross-references."""

    id: UUID
    name: str
    slug: str
    description: str | None = None
    is_active: bool = True


class WorkspaceMembershipInfo(BaseSchema):
    """User's workspace membership details."""

    workspace: BasicWorkspaceInfo
    role: WorkspaceRole
    joined_at: datetime


class WorkspaceMemberInfo(BaseSchema):
    """Workspace member with user information."""

    id: UUID
    user_id: UUID
    workspace_id: UUID
    role: WorkspaceRole
    joined_at: datetime
    invited_by_id: UUID | None = None
    user: BasicUserInfo
