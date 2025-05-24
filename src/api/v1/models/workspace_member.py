"""
WorkspaceMember model - Association table for User and Workspace many-to-many relationship.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.api.v1.models.user import User
    from src.api.v1.models.workspace import Workspace


class WorkspaceRole(str, Enum):
    """Workspace member roles."""

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class WorkspaceMember(SQLModel, table=True):
    """Association model for users and workspaces with roles."""

    __tablename__ = "workspace_members"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    workspace_id: UUID = Field(foreign_key="workspaces.id", nullable=False, index=True)
    role: WorkspaceRole = Field(default=WorkspaceRole.MEMBER, nullable=False)
    joined_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    added_by_id: UUID | None = Field(foreign_key="users.id", default=None)

    # Relationships
    user: "User" = Relationship(
        back_populates="workspace_memberships",
        sa_relationship_kwargs={"foreign_keys": "[WorkspaceMember.user_id]"},
    )
    added_by: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[WorkspaceMember.added_by_id]"}
    )
    workspace: "Workspace" = Relationship(back_populates="members")

    class Config:
        """SQLModel config."""

        # Ensure unique user-workspace combination
        json_schema_extra = {"unique_together": [("user_id", "workspace_id")]}
