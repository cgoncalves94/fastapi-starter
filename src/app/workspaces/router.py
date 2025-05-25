"""
Workspace routes.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.v1.dependencies.authentication import (
    CurrentUser,
    get_current_superuser,
    get_current_user,
)
from app.api.v1.dependencies.authorization import (
    check_workspace_access,
    check_workspace_admin,
)
from app.api.v1.dependencies.services import WorkspaceServiceDep
from app.core.common import PaginatedResponse, PaginationParams
from app.workspaces.schemas import (
    WorkspaceCreate,
    WorkspaceMemberCreate,
    WorkspaceMemberUpdate,
    WorkspaceResponse,
    WorkspaceUpdate,
    WorkspaceWithMemberDetails,
)

router = APIRouter(prefix="/workspaces")


@router.post(
    "/",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["v1 - Workspaces"],
)
async def create_workspace(
    current_user: CurrentUser,
    workspace_data: WorkspaceCreate,
    workspace_service: WorkspaceServiceDep,
) -> WorkspaceResponse:
    """Create a new workspace."""
    return await workspace_service.create_workspace(workspace_data, current_user.id)


@router.get(
    "/all",
    response_model=PaginatedResponse[WorkspaceResponse],
    dependencies=[Depends(get_current_superuser)],
    tags=["v1 - Workspaces"],
)
async def get_all_workspaces(
    workspace_service: WorkspaceServiceDep,
    pagination: PaginationParams = Depends(),
) -> PaginatedResponse[WorkspaceResponse]:
    """Get all workspaces with pagination (superuser only)."""
    return await workspace_service.get_all_workspaces_paginated(pagination)


@router.get(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
    dependencies=[Depends(check_workspace_access)],
    tags=["v1 - Workspaces"],
)
async def get_workspace(
    workspace_id: UUID,
    workspace_service: WorkspaceServiceDep,
) -> WorkspaceResponse:
    """Get workspace by ID."""
    return await workspace_service.get_workspace_by_id(workspace_id)


@router.get(
    "/slug/{slug}",
    response_model=WorkspaceResponse,
    dependencies=[Depends(get_current_user)],
    tags=["v1 - Workspaces"],
)
async def get_workspace_by_slug(
    slug: str,
    workspace_service: WorkspaceServiceDep,
) -> WorkspaceResponse:
    """Get workspace by slug."""
    return await workspace_service.get_workspace_by_slug(slug)


@router.patch(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
    dependencies=[Depends(check_workspace_admin)],
    tags=["v1 - Workspaces"],
)
async def update_workspace(
    workspace_id: UUID,
    workspace_data: WorkspaceUpdate,
    workspace_service: WorkspaceServiceDep,
) -> WorkspaceResponse:
    """Partially update workspace (owner/admin only)."""
    return await workspace_service.update_workspace(workspace_id, workspace_data)


@router.delete(
    "/{workspace_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(check_workspace_admin)],
    tags=["v1 - Workspaces"],
)
async def delete_workspace(
    workspace_id: UUID,
    workspace_service: WorkspaceServiceDep,
) -> None:
    """Delete workspace (owner only)."""
    await workspace_service.delete_workspace(workspace_id)


@router.get(
    "/{workspace_id}/members",
    response_model=WorkspaceWithMemberDetails,
    dependencies=[Depends(check_workspace_access)],
    tags=["v1 - Workspace Members"],
)
async def get_workspace_members(
    workspace_id: UUID,
    workspace_service: WorkspaceServiceDep,
) -> WorkspaceWithMemberDetails:
    """Get workspace with full member details."""
    return await workspace_service.get_workspace_with_member_details(workspace_id)


@router.post(
    "/{workspace_id}/members",
    response_model=WorkspaceResponse,
    dependencies=[Depends(check_workspace_admin)],
    tags=["v1 - Workspace Members"],
)
async def add_workspace_member(
    member_data: WorkspaceMemberCreate,
    workspace_id: UUID,
    current_user: CurrentUser,
    workspace_service: WorkspaceServiceDep,
) -> WorkspaceResponse:
    """Add member to workspace (owner/admin only)."""
    return await workspace_service.add_member(
        workspace_id, member_data, current_user.id
    )


@router.patch(
    "/{workspace_id}/members/{user_id}",
    response_model=WorkspaceResponse,
    dependencies=[Depends(check_workspace_admin)],
    tags=["v1 - Workspace Members"],
)
async def update_member_role(
    workspace_id: UUID,
    user_id: UUID,
    role_data: WorkspaceMemberUpdate,
    current_user: CurrentUser,
    workspace_service: WorkspaceServiceDep,
) -> WorkspaceResponse:
    """Partially update member role in workspace (owner/admin only)."""
    return await workspace_service.update_member_role(
        workspace_id, user_id, role_data, current_user.id
    )


@router.delete(
    "/{workspace_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(check_workspace_admin)],
    tags=["v1 - Workspace Members"],
)
async def remove_workspace_member(
    workspace_id: UUID,
    user_id: UUID,
    workspace_service: WorkspaceServiceDep,
) -> None:
    """Remove member from workspace (owner/admin only, or self-removal)."""
    await workspace_service.remove_member(workspace_id, user_id)


@router.delete(
    "/{workspace_id}/leave",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(check_workspace_access)],
    tags=["v1 - Workspace Members"],
)
async def leave_workspace(
    workspace_id: UUID,
    current_user: CurrentUser,
    workspace_service: WorkspaceServiceDep,
) -> None:
    """Leave workspace (current user removes themselves)."""
    await workspace_service.remove_member(workspace_id, current_user.id)
