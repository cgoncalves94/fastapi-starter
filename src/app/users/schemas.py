"""
User Pydantic schemas.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import EmailStr, Field, SecretStr, model_validator

from app.core.common import BaseSchema, TimestampMixin


class UserBase(BaseSchema):
    """Base user schema."""

    email: EmailStr
    firstname: str | None = Field(None, min_length=2, max_length=50)
    lastname: str | None = Field(None, min_length=2, max_length=50)
    is_active: bool = True
    is_superuser: bool = False


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
    firstname: str | None = Field(None, min_length=2, max_length=50)
    lastname: str | None = Field(None, min_length=2, max_length=50)
    is_active: bool | None = None
    is_superuser: bool | None = None
    password: SecretStr | None = Field(None, min_length=8)


class UserResponse(UserBase, TimestampMixin):
    """Schema for user response."""

    id: UUID


class UserInDB(UserResponse):
    """Schema for user in database."""

    hashed_password: str
