"""
Authentication service with business logic.
"""

from pydantic import EmailStr

from app.auth.schemas import LoginRequest, RegisterRequest, Token
from app.core.exceptions import (
    ConflictError,
    PermissionDeniedError,
)
from app.core.security import (
    create_access_token,
    generate_email_verification_token,
    generate_password_reset_token,
    get_password_hash,
    verify_email_verification_token,
    verify_password,
    verify_password_reset_token,
)
from app.users.repository import UserRepository
from app.users.schemas import UserResponse


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

        # Create user data with hashed password
        user_create_data = {
            "email": user_data.email,
            "firstname": user_data.firstname,
            "lastname": user_data.lastname,
            "hashed_password": get_password_hash(user_data.password.get_secret_value()),
            "is_active": False,  # Require email verification
            "is_superuser": False,
        }

        # Create user
        user = await self.user_repository.create(obj_in=user_create_data)

        # Generate and store email verification token
        verification_token = generate_email_verification_token(user.email)

        # Store token hash in user record for verification
        await self.user_repository.update(
            db_obj=user, obj_in={"pending_verification_token": verification_token}
        )

        # In a real application, you would send an email here
        # For now, we'll just print the token for demonstration
        print(f"Email verification token for {user.email}: {verification_token}")

        return UserResponse.model_validate(user)

    async def login(self, login_data: LoginRequest) -> Token:
        """Authenticate user and return access token."""
        # Get user by email
        user = await self.user_repository.get_by_email(login_data.email)

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

    async def forgot_password(self, email: EmailStr) -> None:
        """Generate a password reset token and send it to the user's email."""
        user = await self.user_repository.get_by_email(email)
        if user:
            token = generate_password_reset_token(user.email)
            # In a real application, you would send an email here
            # For now, we'll just print the token for demonstration
            print(f"Password reset token for {email}: {token}")

    async def reset_password(self, token: str, new_password: str) -> None:
        """Reset user's password using a valid token."""
        email_str = verify_password_reset_token(token)
        if not email_str:
            raise PermissionDeniedError("Invalid or expired password reset token")

        user = await self.user_repository.get_by_email(email_str)
        if not user:
            raise PermissionDeniedError("User not found")

        hashed_password = get_password_hash(new_password)
        await self.user_repository.update(
            db_obj=user, obj_in={"hashed_password": hashed_password}
        )

    async def verify_email(self, token: str) -> None:
        """Verify user's email using a valid token."""
        email_str = verify_email_verification_token(token)
        if not email_str:
            raise PermissionDeniedError("Invalid or expired email verification token")

        user = await self.user_repository.get_by_email(email_str)
        if not user:
            raise PermissionDeniedError("User not found")

        # Check if the token matches the one stored for this user
        if user.pending_verification_token != token:
            raise PermissionDeniedError("Invalid or expired email verification token")

        if user.is_active:
            # Email is already active, no need to re-verify
            return

        # Activate user and clear the verification token
        await self.user_repository.update(
            db_obj=user, obj_in={"is_active": True, "pending_verification_token": None}
        )

    async def send_email_verification(self, email: EmailStr) -> None:
        """Generate and send an email verification token."""
        user = await self.user_repository.get_by_email(email)
        if not user:
            # Don't reveal if email exists or not for security
            return

        if user.is_active:
            # Email already verified
            return

        # Generate verification token
        verification_token = generate_email_verification_token(user.email)

        # Store token in user record for verification
        await self.user_repository.update(
            db_obj=user, obj_in={"pending_verification_token": verification_token}
        )

        # In a real application, you would send an email here
        # For now, we'll just print the token for demonstration
        print(f"Email verification token for {email}: {verification_token}")
