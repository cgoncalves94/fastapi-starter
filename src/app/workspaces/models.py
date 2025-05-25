"""
Workspace models using SQLModel.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.users.models import User


class WorkspaceRole(str, Enum):
    """Workspace member roles."""

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class Workspace(SQLModel, table=True):
    """Workspace model."""

    __tablename__ = "workspaces"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    name: str = Field(nullable=False, index=True)
    slug: str = Field(unique=True, index=True, nullable=False)
    description: str | None = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column_kwargs={
            "onupdate": lambda: datetime.now(UTC)
        },  # auto-update on modify
        nullable=False,
    )

    # Relationships
    members: list["WorkspaceMember"] = Relationship(back_populates="workspace")


class WorkspaceMember(SQLModel, table=True):
    """Association model for users and workspaces with roles."""

    __tablename__ = "workspace_members"
    __table_args__ = (
        UniqueConstraint("user_id", "workspace_id", name="uq_user_workspace"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    workspace_id: UUID = Field(foreign_key="workspaces.id", nullable=False, index=True)
    role: WorkspaceRole = Field(default=WorkspaceRole.MEMBER, nullable=False)
    joined_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), nullable=False
    )
    added_by_email: str | None = Field(default=None)

    # Relationships
    user: "User" = Relationship(back_populates="workspace_memberships")
    workspace: "Workspace" = Relationship(back_populates="members")
