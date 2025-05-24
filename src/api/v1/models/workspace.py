"""
Workspace model using SQLModel.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.api.v1.models.workspace_member import WorkspaceMember


class Workspace(SQLModel, table=True):
    """Workspace model."""

    __tablename__ = "workspaces"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    name: str = Field(nullable=False, index=True)
    slug: str = Field(unique=True, index=True, nullable=False)
    description: str | None = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    members: list["WorkspaceMember"] = Relationship(back_populates="workspace")
