"""
User model using SQLModel.
"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlalchemy import DateTime
from sqlmodel import Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.workspaces.models import WorkspaceMember


class User(SQLModel, table=True):
    """User model."""

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    email: EmailStr = Field(unique=True, index=True, nullable=False)
    firstname: str | None = Field(default=None, max_length=255)
    lastname: str | None = Field(default=None, max_length=255)
    hashed_password: str = Field(nullable=False)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    pending_verification_token: str | None = Field(default=None)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime(timezone=True), nullable=False, onupdate=lambda: datetime.now(UTC)
        ),
    )

    # Relationships
    workspace_memberships: list["WorkspaceMember"] = Relationship(back_populates="user")
