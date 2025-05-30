"""
Authentication Pydantic schemas.
"""

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    SecretStr,
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

    email: EmailStr
    password: SecretStr = Field(..., min_length=8)


class RegisterRequest(BaseModel):
    """Registration request schema."""

    email: EmailStr
    password: SecretStr = Field(..., min_length=8)
    firstname: str | None = Field(None, min_length=2, max_length=50)
    lastname: str | None = Field(None, min_length=2, max_length=50)

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


class ForgotPasswordRequest(BaseModel):
    """Forgot password request schema."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password request schema."""

    token: str
    new_password: SecretStr = Field(..., min_length=8)

    @model_validator(mode="after")
    def validate_password_strength(self) -> "ResetPasswordRequest":
        """Validate password strength after other field validations."""
        if self.new_password:
            password_value = self.new_password.get_secret_value()
            if not any(char.isdigit() for char in password_value):
                raise ValueError("Password must contain at least one digit")
            if not any(char.isupper() for char in password_value):
                raise ValueError("Password must contain at least one uppercase letter")
            if not any(char.islower() for char in password_value):
                raise ValueError("Password must contain at least one lowercase letter")
        return self


class VerifyEmailRequest(BaseModel):
    """Verify email request schema."""

    token: str


class SendEmailVerificationRequest(BaseModel):
    """Send email verification request schema."""

    email: EmailStr


class MessageResponse(BaseModel):
    """Generic message response schema."""

    message: str
