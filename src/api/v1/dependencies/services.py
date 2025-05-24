"""
Service dependencies with proper dependency injection.
"""

from typing import Annotated

from fastapi import Depends

from src.api.v1.dependencies.database import SessionDep
from src.api.v1.repositories.user import UserRepository
from src.api.v1.repositories.workspace import WorkspaceRepository
from src.api.v1.services.auth import AuthService
from src.api.v1.services.user import UserService
from src.api.v1.services.workspace import WorkspaceService


async def get_user_repository(
    session: SessionDep,
) -> UserRepository:
    """Get user repository instance."""
    return UserRepository(session=session)


async def get_workspace_repository(
    session: SessionDep,
) -> WorkspaceRepository:
    """Get workspace repository instance."""
    return WorkspaceRepository(session=session)


async def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    """Get user service instance with dependencies."""
    return UserService(user_repository=user_repository)


async def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> AuthService:
    """Get auth service instance with dependencies."""
    return AuthService(user_repository=user_repository)


async def get_workspace_service(
    user_repository: UserRepository = Depends(get_user_repository),
    workspace_repository: WorkspaceRepository = Depends(get_workspace_repository),
) -> WorkspaceService:
    """Get workspace service instance with dependencies."""
    return WorkspaceService(
        user_repository=user_repository,
        workspace_repository=workspace_repository,
    )


# Type annotations for dependencies
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
WorkspaceServiceDep = Annotated[WorkspaceService, Depends(get_workspace_service)]
