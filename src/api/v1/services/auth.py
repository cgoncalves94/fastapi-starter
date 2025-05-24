"""
Authentication service with business logic.
"""

from src.api.v1.repositories.user import UserRepository
from src.api.v1.schemas.auth import LoginRequest, RegisterRequest, Token
from src.api.v1.schemas.user import UserResponse
from src.core.exceptions import (
    ConflictError,
    PermissionDeniedError,
)
from src.core.security import create_access_token, get_password_hash, verify_password


class AuthService:
    """Authentication service organized by authentication operations."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    # ========================================
    # AUTHENTICATION OPERATIONS
    # ========================================

    async def register(self, user_data: RegisterRequest) -> UserResponse:
        """Register a new user."""
        # Check if email is already taken
        if await self.user_repository.get_by_email(user_data.email):
            raise ConflictError("Email already registered")

        # Check if username is already taken
        if await self.user_repository.get_by_username(user_data.username):
            raise ConflictError("Username already taken")

        # Create user data with hashed password
        user_create_data = {
            "email": user_data.email,
            "username": user_data.username.lower(),
            "full_name": user_data.full_name,
            "hashed_password": get_password_hash(user_data.password.get_secret_value()),
            "is_active": True,
            "is_superuser": False,
        }

        # Create user
        user = await self.user_repository.create(obj_in=user_create_data)
        return UserResponse.model_validate(user)

    async def login(self, login_data: LoginRequest) -> Token:
        """Authenticate user and return access token."""
        # Get user by email or username
        user = await self.user_repository.get_by_email_or_username(login_data.username)

        if not user:
            raise PermissionDeniedError("Invalid credentials")

        if not user.is_active:
            raise PermissionDeniedError("User account is inactive")

        # Verify password
        if not verify_password(
            login_data.password.get_secret_value(), user.hashed_password
        ):
            raise PermissionDeniedError("Invalid credentials")

        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})

        return Token(access_token=access_token)
