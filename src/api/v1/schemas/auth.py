"""
Authentication Pydantic schemas.
"""

from pydantic import (
    BaseModel,
    EmailStr,
    SecretStr,
    Field,
    field_validator,
    model_validator,
)


class Token(BaseModel):
    """Token response schema."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema."""

    sub: str | None = None


class LoginRequest(BaseModel):
    """Login request schema."""

    username: str = Field(..., min_length=3, max_length=50)
    password: SecretStr = Field(..., min_length=8)


class RegisterRequest(BaseModel):
    """Registration request schema."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: SecretStr = Field(..., min_length=8)
    full_name: str | None = None

    @classmethod
    @field_validator("username")
    def validate_username(cls, v: str) -> str:
        """Validate username format. Pydantic's @field_validator makes this a class method implicitly."""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "Username must contain only letters, numbers, underscores, and hyphens"
            )
        return v.lower()

    @model_validator(mode="after")
    def validate_password_strength(self) -> "RegisterRequest":
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
