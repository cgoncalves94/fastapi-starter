"""
User service with business logic.
"""

import math
from uuid import UUID

from app.core.common import PaginatedResponse, PaginationParams
from app.core.exceptions import ConflictError, NotFoundError
from app.core.security import get_password_hash
from app.users.repository import UserRepository
from app.users.schemas import UserCreate, UserResponse, UserUpdate


class UserService:
    """User service organized by CRUD operations."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    # ========================================
    # USER CRUD OPERATIONS
    # ========================================

    # CREATE
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user."""
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
            "is_active": user_data.is_active,
            "is_superuser": user_data.is_superuser,
        }

        # Create user
        user = await self.user_repository.create(obj_in=user_create_data)
        return UserResponse.model_validate(user)

    # READ
    async def get_user_by_id(self, user_id: UUID) -> UserResponse:
        """Get user by ID."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return UserResponse.model_validate(user)

    async def get_users_paginated(
        self, pagination: PaginationParams
    ) -> PaginatedResponse[UserResponse]:
        """Get paginated list of users."""
        # Get users with pagination
        users = await self.user_repository.get_multi(
            skip=pagination.offset, limit=pagination.per_page
        )

        # Get total count
        total = await self.user_repository.count()

        # Calculate total pages
        pages = math.ceil(total / pagination.per_page) if total > 0 else 0

        # Convert to response models
        user_responses = [UserResponse.model_validate(user) for user in users]

        return PaginatedResponse[UserResponse](
            items=user_responses,
            total=total,
            page=pagination.page,
            per_page=pagination.per_page,
            pages=pages,
        )

    # UPDATE
    async def update_user(self, user_id: UUID, user_data: UserUpdate) -> UserResponse:
        """Update user."""
        # Get existing user
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        # Get only the fields that were actually provided
        update_data = user_data.model_dump(exclude_unset=True)

        # Handle special validations for unique fields
        if "email" in update_data and update_data["email"] != user.email:
            if await self.user_repository.is_email_taken(
                update_data["email"], exclude_id=user_id
            ):
                raise ConflictError("Email already registered")

        if "username" in update_data and update_data["username"] != user.username:
            if await self.user_repository.is_username_taken(
                update_data["username"], exclude_id=user_id
            ):
                raise ConflictError("Username already taken")
            update_data["username"] = update_data["username"].lower()

        # Handle password hashing
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(
                user_data.password.get_secret_value()
            )
            del update_data["password"]

        # Update user
        updated_user = await self.user_repository.update(
            db_obj=user, obj_in=update_data
        )
        return UserResponse.model_validate(updated_user)

    async def deactivate_user(self, user_id: UUID) -> UserResponse:
        """Deactivate user instead of deleting."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        updated_user = await self.user_repository.update(
            db_obj=user, obj_in={"is_active": False}
        )
        return UserResponse.model_validate(updated_user)

    # DELETE
    async def delete_user(self, user_id: UUID) -> None:
        """Delete user."""
        user = await self.user_repository.delete(id=user_id)
        if not user:
            raise NotFoundError("User not found")
