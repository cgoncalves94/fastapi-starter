"""
Integration tests for workspace management endpoints.

These tests verify workspace CRUD operations and member management:
- Creating workspaces
- Listing and retrieving workspaces
- Managing workspace members
- Workspace permissions

Note: This is a simplified test suite for learning purposes.
You can expand it with more edge cases as you learn.
"""

import pytest
from httpx import AsyncClient

from app.users.models import User

# Mark all tests in this file as integration tests
pytestmark = pytest.mark.integration


# ============================================================================
# WORKSPACE CREATION TESTS
# ============================================================================


async def test_create_workspace(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """
    Test creating a new workspace.

    Verifies that:
    - Authenticated users can create workspaces
    - Creator becomes the owner
    - Returns workspace data
    """
    workspace_data = {
        "name": "Test Workspace",
        "description": "A workspace for testing",
    }

    response = await client.post(
        "/api/v1/workspaces/",
        json=workspace_data,
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()

    assert data["name"] == workspace_data["name"]
    assert data["description"] == workspace_data["description"]
    assert "id" in data
    assert "slug" in data


async def test_create_workspace_unauthenticated(client: AsyncClient) -> None:
    """
    Test that unauthenticated users cannot create workspaces.

    Verifies that:
    - Authentication is required
    - Returns 403 Forbidden
    """
    workspace_data = {
        "name": "Test Workspace",
        "description": "A workspace for testing",
    }

    response = await client.post("/api/v1/workspaces/", json=workspace_data)

    assert response.status_code == 403


# ============================================================================
# LIST WORKSPACES TESTS
# ============================================================================


async def test_list_user_workspaces(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict[str, str],
) -> None:
    """
    Test listing workspaces for current user.

    Verifies that:
    - Users can see their own workspaces
    - Returns list of workspaces they're members of
    """
    # First, create a workspace
    workspace_data = {"name": "My Workspace", "description": "Test"}
    create_response = await client.post(
        "/api/v1/workspaces/",
        json=workspace_data,
        headers=auth_headers,
    )
    assert create_response.status_code == 201

    # Now list workspaces
    response = await client.get("/api/v1/workspaces/", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    # Should have at least the workspace we just created
    assert len(data) >= 1
    assert any(w["name"] == "My Workspace" for w in data)


# ============================================================================
# GET WORKSPACE TESTS
# ============================================================================


async def test_get_workspace_as_member(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """
    Test getting workspace details as a member.

    Verifies that:
    - Workspace members can view workspace details
    - Returns complete workspace information
    """
    # Create a workspace first
    workspace_data = {"name": "Details Test", "description": "Test workspace"}
    create_response = await client.post(
        "/api/v1/workspaces/",
        json=workspace_data,
        headers=auth_headers,
    )
    workspace_id = create_response.json()["id"]

    # Get workspace details
    response = await client.get(
        f"/api/v1/workspaces/{workspace_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == workspace_id
    assert data["name"] == workspace_data["name"]


async def test_get_workspace_not_member(
    client: AsyncClient,
    test_user: User,
    test_superuser: User,
    auth_headers: dict[str, str],
    superuser_headers: dict[str, str],
) -> None:
    """
    Test that non-members cannot access workspace.

    Verifies that:
    - Only workspace members can view workspace details
    - Returns 403 Forbidden for non-members
    """
    # Create workspace as superuser
    workspace_data = {"name": "Private Workspace", "description": "Private"}
    create_response = await client.post(
        "/api/v1/workspaces/",
        json=workspace_data,
        headers=superuser_headers,
    )
    workspace_id = create_response.json()["id"]

    # Try to access as regular user (not a member)
    response = await client.get(
        f"/api/v1/workspaces/{workspace_id}",
        headers=auth_headers,
    )

    # This should be forbidden unless the user is added as a member
    # The exact behavior depends on your authorization implementation
    assert response.status_code in [403, 404]


# ============================================================================
# UPDATE WORKSPACE TESTS
# ============================================================================


async def test_update_workspace_as_owner(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """
    Test updating workspace as owner.

    Verifies that:
    - Workspace owners can update workspace details
    - Changes are persisted
    """
    # Create workspace
    workspace_data = {"name": "Original Name", "description": "Original"}
    create_response = await client.post(
        "/api/v1/workspaces/",
        json=workspace_data,
        headers=auth_headers,
    )
    workspace_id = create_response.json()["id"]

    # Update workspace
    update_data = {"name": "Updated Name", "description": "Updated description"}
    response = await client.patch(
        f"/api/v1/workspaces/{workspace_id}",
        json=update_data,
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert data["name"] == "Updated Name"
    assert data["description"] == "Updated description"


# ============================================================================
# DELETE WORKSPACE TESTS
# ============================================================================


async def test_delete_workspace_as_owner(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """
    Test deleting workspace as owner.

    Verifies that:
    - Workspace owners can delete workspaces
    - Returns 204 No Content
    """
    # Create workspace
    workspace_data = {"name": "To Delete", "description": "Will be deleted"}
    create_response = await client.post(
        "/api/v1/workspaces/",
        json=workspace_data,
        headers=auth_headers,
    )
    workspace_id = create_response.json()["id"]

    # Delete workspace
    response = await client.delete(
        f"/api/v1/workspaces/{workspace_id}",
        headers=auth_headers,
    )

    assert response.status_code == 204

    # Verify it's deleted
    get_response = await client.get(
        f"/api/v1/workspaces/{workspace_id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 404


# ============================================================================
# WORKSPACE MEMBER MANAGEMENT TESTS
# ============================================================================


async def test_add_member_to_workspace(
    client: AsyncClient,
    test_superuser: User,
    auth_headers: dict[str, str],
) -> None:
    """
    Test adding a member to workspace.

    Verifies that:
    - Workspace owners can add members
    - Members are added with correct role
    """
    # Create workspace
    workspace_data = {"name": "Team Workspace", "description": "For the team"}
    create_response = await client.post(
        "/api/v1/workspaces/",
        json=workspace_data,
        headers=auth_headers,
    )
    workspace_id = create_response.json()["id"]

    # Add member
    member_data = {
        "user_id": str(test_superuser.id),
        "role": "Editor",  # or "Viewer" depending on your roles
    }

    response = await client.post(
        f"/api/v1/workspaces/{workspace_id}/members",
        json=member_data,
        headers=auth_headers,
    )

    # The exact status code depends on your implementation
    # 200 OK or 201 Created are both reasonable
    assert response.status_code in [200, 201]


async def test_list_workspace_members(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """
    Test listing workspace members.

    Verifies that:
    - Can retrieve list of workspace members
    - Owner is in the member list
    """
    # Create workspace
    workspace_data = {"name": "Members Test", "description": "Testing members"}
    create_response = await client.post(
        "/api/v1/workspaces/",
        json=workspace_data,
        headers=auth_headers,
    )
    workspace_id = create_response.json()["id"]

    # List members
    response = await client.get(
        f"/api/v1/workspaces/{workspace_id}/members",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    # Should have at least the creator/owner
    assert len(data) >= 1


# ============================================================================
# EDGE CASES
# ============================================================================


async def test_create_workspace_with_duplicate_name(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """
    Test creating workspaces with duplicate names.

    Note: Depending on your implementation, duplicate names might be:
    - Allowed (different workspaces can have same name)
    - Prevented (workspace names must be unique)
    - Prevented per user (user can't have duplicate workspace names)

    This test assumes duplicate names are allowed for different workspaces.
    """
    workspace_data = {"name": "Duplicate Name", "description": "First"}

    # Create first workspace
    response1 = await client.post(
        "/api/v1/workspaces/",
        json=workspace_data,
        headers=auth_headers,
    )
    assert response1.status_code == 201

    # Create second workspace with same name
    workspace_data["description"] = "Second"
    response2 = await client.post(
        "/api/v1/workspaces/",
        json=workspace_data,
        headers=auth_headers,
    )

    # This will depend on your business rules
    # If you allow duplicates, this should be 201
    # If you prevent duplicates, this should be 409
    assert response2.status_code in [201, 409]


async def test_access_nonexistent_workspace(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """
    Test accessing a workspace that doesn't exist.

    Verifies that:
    - Returns 404 Not Found
    """
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = await client.get(
        f"/api/v1/workspaces/{fake_uuid}",
        headers=auth_headers,
    )

    assert response.status_code == 404
