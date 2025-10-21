"""
Integration tests for user management endpoints.

These tests verify user CRUD operations and authorization:
- Creating users (admin only)
- Listing users with pagination (admin only)
- Getting user details
- Updating user information
- Deactivating users (admin only)
- Deleting users (admin only)
"""

from typing import Any

import pytest
from httpx import AsyncClient

from app.users.models import User

# Mark all tests in this file as integration tests
pytestmark = pytest.mark.integration


# ============================================================================
# CREATE USER TESTS (SUPERUSER ONLY)
# ============================================================================


async def test_create_user_as_superuser(
    client: AsyncClient,
    superuser_headers: dict[str, str],
    sample_user_data: dict[str, Any],
) -> None:
    """
    Test creating a new user as superuser.

    Verifies that:
    - Superusers can create new users
    - Response contains created user data
    - Returns 201 Created status
    """
    response = await client.post(
        "/api/v1/users/",
        json=sample_user_data,
        headers=superuser_headers,
    )

    assert response.status_code == 201
    data = response.json()

    assert data["email"] == sample_user_data["email"]
    assert data["firstname"] == sample_user_data["firstname"]
    assert data["lastname"] == sample_user_data["lastname"]
    assert "id" in data


async def test_create_user_as_regular_user(
    client: AsyncClient,
    auth_headers: dict[str, str],
    sample_user_data: dict[str, Any],
) -> None:
    """
    Test that regular users cannot create users.

    Verifies that:
    - Only superusers can create users
    - Returns 403 Forbidden for regular users
    """
    response = await client.post(
        "/api/v1/users/",
        json=sample_user_data,
        headers=auth_headers,
    )

    assert response.status_code == 403


async def test_create_user_unauthenticated(
    client: AsyncClient,
    sample_user_data: dict[str, Any],
) -> None:
    """
    Test that unauthenticated requests cannot create users.

    Verifies that:
    - Authentication is required
    - Returns 403 Forbidden
    """
    response = await client.post("/api/v1/users/", json=sample_user_data)

    assert response.status_code == 403


# ============================================================================
# LIST USERS TESTS (SUPERUSER ONLY)
# ============================================================================


async def test_list_users_as_superuser(
    client: AsyncClient,
    test_user: User,
    test_superuser: User,
    superuser_headers: dict[str, str],
) -> None:
    """
    Test listing users with pagination as superuser.

    Verifies that:
    - Superusers can list all users
    - Response includes pagination metadata
    - Returns correct user data
    """
    response = await client.get("/api/v1/users/", headers=superuser_headers)

    assert response.status_code == 200
    data = response.json()

    # Verify pagination structure
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data
    assert "pages" in data

    # Should have at least our test users
    assert data["total"] >= 2
    assert len(data["items"]) >= 2


async def test_list_users_pagination(
    client: AsyncClient,
    test_user: User,
    test_superuser: User,
    superuser_headers: dict[str, str],
) -> None:
    """
    Test pagination parameters work correctly.

    Verifies that:
    - Page and size parameters are respected
    - Pagination metadata is accurate
    """
    # Request first page with size of 1
    response = await client.get(
        "/api/v1/users/?page=1&size=1",
        headers=superuser_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert data["page"] == 1
    assert data["size"] == 1
    assert len(data["items"]) == 1
    assert data["total"] >= 2


async def test_list_users_as_regular_user(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """
    Test that regular users cannot list all users.

    Verifies that:
    - Only superusers can list users
    - Returns 403 Forbidden
    """
    response = await client.get("/api/v1/users/", headers=auth_headers)

    assert response.status_code == 403


# ============================================================================
# GET USER BY ID TESTS
# ============================================================================


async def test_get_own_user(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict[str, str],
) -> None:
    """
    Test that users can get their own information.

    Verifies that:
    - Users can access their own profile
    - Returns complete user data
    """
    response = await client.get(
        f"/api/v1/users/{test_user.id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == test_user.id
    assert data["email"] == test_user.email


async def test_get_other_user_as_regular_user(
    client: AsyncClient,
    test_user: User,
    test_superuser: User,
    auth_headers: dict[str, str],
) -> None:
    """
    Test that regular users cannot access other users' profiles.

    Verifies that:
    - Users can only access their own profile
    - Returns 403 Forbidden when accessing others
    """
    response = await client.get(
        f"/api/v1/users/{test_superuser.id}",
        headers=auth_headers,
    )

    assert response.status_code == 403


async def test_get_any_user_as_superuser(
    client: AsyncClient,
    test_user: User,
    superuser_headers: dict[str, str],
) -> None:
    """
    Test that superusers can access any user's profile.

    Verifies that:
    - Superusers can view any user
    - Returns user data
    """
    response = await client.get(
        f"/api/v1/users/{test_user.id}",
        headers=superuser_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == test_user.id


async def test_get_nonexistent_user(
    client: AsyncClient,
    superuser_headers: dict[str, str],
) -> None:
    """
    Test getting a user that doesn't exist.

    Verifies that:
    - Returns 404 Not Found for nonexistent users
    """
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = await client.get(
        f"/api/v1/users/{fake_uuid}",
        headers=superuser_headers,
    )

    assert response.status_code == 404


# ============================================================================
# GET USER WITH WORKSPACES TESTS
# ============================================================================


async def test_get_own_user_workspaces(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict[str, str],
) -> None:
    """
    Test getting own user profile with workspace memberships.

    Verifies that:
    - Users can see their own workspaces
    - Response includes workspace data
    """
    response = await client.get(
        f"/api/v1/users/{test_user.id}/workspaces",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == test_user.id
    assert "workspaces" in data


async def test_get_other_user_workspaces_forbidden(
    client: AsyncClient,
    test_superuser: User,
    auth_headers: dict[str, str],
) -> None:
    """
    Test that regular users cannot see other users' workspaces.

    Verifies that:
    - Users can only see their own workspace memberships
    - Returns 403 Forbidden
    """
    response = await client.get(
        f"/api/v1/users/{test_superuser.id}/workspaces",
        headers=auth_headers,
    )

    assert response.status_code == 403


# ============================================================================
# UPDATE USER TESTS
# ============================================================================


async def test_update_own_user(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict[str, str],
) -> None:
    """
    Test that users can update their own profile.

    Verifies that:
    - Users can update their own information
    - Changes are persisted
    - Returns updated user data
    """
    update_data = {
        "firstname": "Updated",
        "lastname": "Name",
    }

    response = await client.patch(
        f"/api/v1/users/{test_user.id}",
        json=update_data,
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert data["firstname"] == "Updated"
    assert data["lastname"] == "Name"
    assert data["email"] == test_user.email  # Email unchanged


async def test_update_other_user_forbidden(
    client: AsyncClient,
    test_superuser: User,
    auth_headers: dict[str, str],
) -> None:
    """
    Test that regular users cannot update other users' profiles.

    Verifies that:
    - Users can only update their own profile
    - Returns 403 Forbidden
    """
    update_data = {"firstname": "Hacker"}

    response = await client.patch(
        f"/api/v1/users/{test_superuser.id}",
        json=update_data,
        headers=auth_headers,
    )

    assert response.status_code == 403


async def test_update_user_as_superuser(
    client: AsyncClient,
    test_user: User,
    superuser_headers: dict[str, str],
) -> None:
    """
    Test that superusers can update any user's profile.

    Verifies that:
    - Superusers can update any user
    - Changes are applied correctly
    """
    update_data = {"firstname": "AdminUpdated"}

    response = await client.patch(
        f"/api/v1/users/{test_user.id}",
        json=update_data,
        headers=superuser_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert data["firstname"] == "AdminUpdated"


async def test_partial_update_user(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict[str, str],
) -> None:
    """
    Test partial update (PATCH) with only one field.

    Verifies that:
    - Partial updates work correctly
    - Other fields remain unchanged
    """
    original_lastname = test_user.lastname

    update_data = {"firstname": "OnlyFirstname"}

    response = await client.patch(
        f"/api/v1/users/{test_user.id}",
        json=update_data,
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert data["firstname"] == "OnlyFirstname"
    assert data["lastname"] == original_lastname


# ============================================================================
# DEACTIVATE USER TESTS (SUPERUSER ONLY)
# ============================================================================


async def test_deactivate_user_as_superuser(
    client: AsyncClient,
    test_user: User,
    superuser_headers: dict[str, str],
) -> None:
    """
    Test deactivating a user as superuser.

    Verifies that:
    - Superusers can deactivate users
    - User is marked as inactive
    """
    response = await client.patch(
        f"/api/v1/users/{test_user.id}/deactivate",
        headers=superuser_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert data["is_active"] is False


async def test_deactivate_user_as_regular_user(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict[str, str],
) -> None:
    """
    Test that regular users cannot deactivate users.

    Verifies that:
    - Only superusers can deactivate users
    - Returns 403 Forbidden
    """
    response = await client.patch(
        f"/api/v1/users/{test_user.id}/deactivate",
        headers=auth_headers,
    )

    assert response.status_code == 403


# ============================================================================
# DELETE USER TESTS (SUPERUSER ONLY)
# ============================================================================


async def test_delete_user_as_superuser(
    client: AsyncClient,
    test_user: User,
    superuser_headers: dict[str, str],
) -> None:
    """
    Test deleting a user as superuser.

    Verifies that:
    - Superusers can delete users
    - Returns 204 No Content
    """
    response = await client.delete(
        f"/api/v1/users/{test_user.id}",
        headers=superuser_headers,
    )

    assert response.status_code == 204

    # Verify user is actually deleted
    get_response = await client.get(
        f"/api/v1/users/{test_user.id}",
        headers=superuser_headers,
    )
    assert get_response.status_code == 404


async def test_delete_user_as_regular_user(
    client: AsyncClient,
    test_superuser: User,
    auth_headers: dict[str, str],
) -> None:
    """
    Test that regular users cannot delete users.

    Verifies that:
    - Only superusers can delete users
    - Returns 403 Forbidden
    """
    response = await client.delete(
        f"/api/v1/users/{test_superuser.id}",
        headers=auth_headers,
    )

    assert response.status_code == 403


async def test_delete_nonexistent_user(
    client: AsyncClient,
    superuser_headers: dict[str, str],
) -> None:
    """
    Test deleting a user that doesn't exist.

    Verifies that:
    - Returns 404 Not Found
    """
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = await client.delete(
        f"/api/v1/users/{fake_uuid}",
        headers=superuser_headers,
    )

    assert response.status_code == 404


# ============================================================================
# AUTHORIZATION EDGE CASES
# ============================================================================


async def test_access_with_expired_token(client: AsyncClient) -> None:
    """
    Test access with an expired token.

    Note: This test would require generating an expired token.
    For a learning project, we just verify invalid tokens are rejected.
    """
    headers = {"Authorization": "Bearer expired_or_invalid_token"}
    response = await client.get("/api/v1/users/", headers=headers)

    assert response.status_code == 401


async def test_access_with_malformed_auth_header(client: AsyncClient) -> None:
    """
    Test access with malformed Authorization header.

    Verifies that:
    - Malformed headers are rejected
    - Returns 403 Forbidden
    """
    headers = {"Authorization": "InvalidFormat"}
    response = await client.get("/api/v1/users/", headers=headers)

    assert response.status_code == 403
