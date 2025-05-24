"""
Authorization dependencies for route-level access control.
"""

from uuid import UUID

from fastapi import HTTPException, Path, status

from app.api.v1.dependencies.authentication import CurrentUser
from app.api.v1.dependencies.services import WorkspaceServiceDep
from app.workspaces.models import WorkspaceRole


def check_user_access(
    current_user: CurrentUser,
    user_id: UUID = Path(..., title="User ID", description="The ID of the user."),
):
    """User can access their own profile or is superuser."""
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )


async def check_workspace_access(
    current_user: CurrentUser,
    workspace_service: WorkspaceServiceDep,
    workspace_id: UUID = Path(
        ..., title="Workspace ID", description="The ID of the workspace."
    ),
):
    """User must be a member of the workspace or be a superuser."""
    # Superusers can access any workspace
    if current_user.is_superuser:
        return

    # Check if workspace exists first
    workspace = await workspace_service.workspace_repository.get_by_id(workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    user_role = await workspace_service.workspace_repository.get_user_role_in_workspace(
        workspace_id, current_user.id
    )
    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this workspace",
        )


async def check_workspace_admin(
    current_user: CurrentUser,
    workspace_service: WorkspaceServiceDep,
    workspace_id: UUID = Path(
        ..., title="Workspace ID", description="The ID of the workspace."
    ),
):
    """User must be admin or owner of the workspace, or be a superuser."""
    # Superusers can access any workspace
    if current_user.is_superuser:
        return

    # Check if workspace exists first
    workspace = await workspace_service.workspace_repository.get_by_id(workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    user_role = await workspace_service.workspace_repository.get_user_role_in_workspace(
        workspace_id, current_user.id
    )
    if user_role not in [WorkspaceRole.OWNER, WorkspaceRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or owner access required",
        )
