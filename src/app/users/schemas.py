"""
User Pydantic schemas.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import EmailStr, Field, SecretStr, field_validator, model_validator

from app.core.common import BaseSchema, TimestampMixin
from app.core.shared import WorkspaceMembershipInfo


class UserBase(BaseSchema):
    """Base user schema."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str | None = None
    is_active: bool = True
    is_superuser: bool = False

    @classmethod
    @field_validator("username")
    def validate_username(cls, v: str) -> str:
        """Validate username format."""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "Username must contain only letters, numbers, underscores, and hyphens"
            )
        return v.lower()


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: SecretStr = Field(..., min_length=8)

    @model_validator(mode="after")
    def validate_password_strength(self) -> UserCreate:
        """Validate password strength after other field validations."""
        if self.password:
            password_value = self.password.get_secret_value()
            if not any(char.isdigit() for char in password_value):
                raise ValueError("Password must contain at least one digit")
            if not any(char.isupper() for char in password_value):
                raise ValueError("Password must contain at least one uppercase letter")
            if not any(char.islower() for char in password_value):
                raise ValueError("Password must contain at least one lowercase letter")
        return self


class UserUpdate(BaseSchema):
    """Schema for updating a user."""

    email: EmailStr | None = None
    username: str | None = Field(None, min_length=3, max_length=50)
    full_name: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    password: SecretStr | None = Field(None, min_length=8)


class UserResponse(UserBase, TimestampMixin):
    """Schema for user response."""

    id: UUID


class UserInDB(UserResponse):
    """Schema for user in database."""

    hashed_password: str


class UserWithWorkspaces(UserResponse):
    """User with workspaces information."""

    workspaces: list[WorkspaceMembershipInfo] = Field(default_factory=list)
