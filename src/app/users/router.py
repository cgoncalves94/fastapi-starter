"""
User routes.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.v1.dependencies.authentication import (
    get_current_superuser,
)
from app.api.v1.dependencies.authorization import check_user_access
from app.api.v1.dependencies.services import UserServiceDep
from app.core.common import PaginatedResponse, PaginationParams
from app.users.schemas import (
    UserCreate,
    UserResponse,
    UserResponseWithWorkspaces,
    UserUpdate,
)

router = APIRouter(prefix="/users", tags=["v1 - Users"])


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_superuser)],
)
async def create_user(
    user_data: UserCreate,
    user_service: UserServiceDep,
) -> UserResponse:
    """Create a new user (superuser only)."""
    return await user_service.create_user(user_data)


@router.get(
    "/",
    response_model=PaginatedResponse[UserResponse],
    dependencies=[Depends(get_current_superuser)],
)
async def get_users(
    user_service: UserServiceDep,
    pagination: PaginationParams = Depends(),
) -> PaginatedResponse[UserResponse]:
    """Get list of users with pagination (superuser only)."""
    return await user_service.get_users_paginated(pagination)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(check_user_access)],
)
async def get_user(
    user_id: UUID,
    user_service: UserServiceDep,
) -> UserResponse:
    """Get user by ID. Users can only access their own profile unless they're superuser."""
    return await user_service.get_user_by_id(user_id)


@router.get(
    "/{user_id}/workspaces",
    response_model=UserResponseWithWorkspaces,
    dependencies=[Depends(check_user_access)],
)
async def get_user_workspaces(
    user_id: UUID,
    user_service: UserServiceDep,
) -> UserResponseWithWorkspaces:
    """Get user with their workspace memberships. Users can only access their own unless they're superuser."""
    return await user_service.get_user_with_workspaces(user_id)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(check_user_access)],
)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    user_service: UserServiceDep,
) -> UserResponse:
    """Partially update user. Users can only update their own profile unless they're superuser."""
    return await user_service.update_user(user_id, user_data)


@router.patch(
    "/{user_id}/deactivate",
    response_model=UserResponse,
    dependencies=[Depends(get_current_superuser)],
)
async def deactivate_user(
    user_id: UUID,
    user_service: UserServiceDep,
) -> UserResponse:
    """Deactivate user (superuser only)."""
    return await user_service.deactivate_user(user_id)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_superuser)],
)
async def delete_user(
    user_id: UUID,
    user_service: UserServiceDep,
) -> None:
    """Delete user (superuser only)."""
    await user_service.delete_user(user_id)
