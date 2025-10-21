"""
Integration tests for authentication endpoints.

These tests verify the authentication flow including:
- User registration
- Login/logout
- Token validation
- Email verification
- Password reset

Learn more about testing FastAPI: https://fastapi.tiangolo.com/tutorial/testing/
"""

from typing import Any

import pytest
from httpx import AsyncClient

from app.users.models import User

# Mark all tests in this file as integration tests
pytestmark = pytest.mark.integration


# ============================================================================
# REGISTRATION TESTS
# ============================================================================


async def test_register_new_user(
    client: AsyncClient,
    sample_user_data: dict[str, Any],
) -> None:
    """
    Test successful user registration.

    Verifies that:
    - New user can be registered with valid data
    - Response contains user data (without password)
    - Returns 201 Created status
    """
    response = await client.post("/api/v1/auth/register", json=sample_user_data)

    assert response.status_code == 201
    data = response.json()

    # Verify response structure
    assert "id" in data
    assert data["email"] == sample_user_data["email"]
    assert data["firstname"] == sample_user_data["firstname"]
    assert data["lastname"] == sample_user_data["lastname"]
    assert data["is_active"] is True
    assert data["is_superuser"] is False

    # Ensure password is NOT returned in response
    assert "password" not in data
    assert "hashed_password" not in data


async def test_register_duplicate_email(
    client: AsyncClient,
    test_user: User,
    sample_user_data: dict[str, Any],
) -> None:
    """
    Test registration with an already registered email.

    Verifies that:
    - Cannot register with an email that's already in use
    - Returns appropriate error status (409 Conflict)
    """
    # Try to register with the same email as test_user
    sample_user_data["email"] = test_user.email

    response = await client.post("/api/v1/auth/register", json=sample_user_data)

    assert response.status_code == 409
    data = response.json()
    assert "already registered" in data["detail"].lower()


async def test_register_invalid_email(
    client: AsyncClient,
    sample_user_data: dict[str, Any],
) -> None:
    """
    Test registration with invalid email format.

    Verifies that:
    - Registration fails with malformed email
    - Returns validation error (422 Unprocessable Entity)
    """
    sample_user_data["email"] = "not-a-valid-email"

    response = await client.post("/api/v1/auth/register", json=sample_user_data)

    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


async def test_register_missing_fields(client: AsyncClient) -> None:
    """
    Test registration with missing required fields.

    Verifies that all required fields are validated.
    """
    incomplete_data = {
        "email": "test@example.com",
        # Missing firstname, lastname, password
    }

    response = await client.post("/api/v1/auth/register", json=incomplete_data)

    assert response.status_code == 422


# ============================================================================
# LOGIN TESTS
# ============================================================================


async def test_login_success(
    client: AsyncClient,
    test_user: User,
    user_password: str,
) -> None:
    """
    Test successful user login.

    Verifies that:
    - User can login with correct credentials
    - Response contains access token
    - Token type is 'bearer'
    """
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": user_password},
    )

    assert response.status_code == 200
    data = response.json()

    # Verify token structure
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


async def test_login_wrong_password(
    client: AsyncClient,
    test_user: User,
) -> None:
    """
    Test login with incorrect password.

    Verifies that:
    - Login fails with wrong password
    - Returns 401 Unauthorized
    """
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "WrongPassword123!"},
    )

    assert response.status_code == 401
    data = response.json()
    assert "incorrect" in data["detail"].lower()


async def test_login_nonexistent_user(client: AsyncClient) -> None:
    """
    Test login with email that doesn't exist.

    Verifies that:
    - Login fails for non-existent users
    - Returns 401 Unauthorized (same as wrong password for security)
    """
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@example.com", "password": "SomePassword123!"},
    )

    assert response.status_code == 401


async def test_login_inactive_user(
    client: AsyncClient,
    inactive_user: User,
    user_password: str,
) -> None:
    """
    Test login with an inactive user account.

    Verifies that:
    - Inactive users cannot login
    - Returns appropriate error
    """
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": inactive_user.email, "password": user_password},
    )

    assert response.status_code == 403
    data = response.json()
    assert "inactive" in data["detail"].lower() or "not active" in data["detail"].lower()


# ============================================================================
# GET CURRENT USER TESTS
# ============================================================================


async def test_get_current_user_authenticated(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict[str, str],
) -> None:
    """
    Test retrieving current user information with valid token.

    Verifies that:
    - Authenticated users can get their own information
    - Response contains complete user data
    """
    response = await client.get("/api/v1/auth/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == test_user.id
    assert data["email"] == test_user.email
    assert data["firstname"] == test_user.firstname
    assert data["lastname"] == test_user.lastname


async def test_get_current_user_no_token(client: AsyncClient) -> None:
    """
    Test retrieving current user without authentication.

    Verifies that:
    - Unauthenticated requests are rejected
    - Returns 401 Unauthorized
    """
    response = await client.get("/api/v1/auth/me")

    assert response.status_code == 401


async def test_get_current_user_invalid_token(client: AsyncClient) -> None:
    """
    Test retrieving current user with invalid token.

    Verifies that:
    - Invalid tokens are rejected
    - Returns 401 Unauthorized
    """
    headers = {"Authorization": "Bearer invalid_token_here"}
    response = await client.get("/api/v1/auth/me", headers=headers)

    assert response.status_code == 401


# ============================================================================
# EMAIL VERIFICATION TESTS
# ============================================================================


async def test_send_email_verification(
    client: AsyncClient,
    test_user: User,
) -> None:
    """
    Test sending email verification token.

    Note: In a real application, this would send an actual email.
    For this starter project, we just verify the endpoint works.

    Verifies that:
    - Email verification can be requested
    - Returns success message
    """
    response = await client.post(
        "/api/v1/auth/send-email-verification",
        json={"email": test_user.email},
    )

    assert response.status_code == 200
    data = response.json()
    assert "message" in data


async def test_send_email_verification_nonexistent_email(
    client: AsyncClient,
) -> None:
    """
    Test sending verification to non-existent email.

    Verifies that:
    - Returns success even for non-existent emails (security best practice)
    - Prevents email enumeration attacks
    """
    response = await client.post(
        "/api/v1/auth/send-email-verification",
        json={"email": "nonexistent@example.com"},
    )

    # Should still return 200 to prevent email enumeration
    assert response.status_code == 200


# Note: Testing email verification with token requires implementing
# token generation in the AuthService. This is left as an exercise
# for learning purposes. You would need to:
# 1. Generate a verification token
# 2. Store it in the database or cache
# 3. Verify it in the verify-email endpoint


# ============================================================================
# PASSWORD RESET TESTS
# ============================================================================


async def test_forgot_password(
    client: AsyncClient,
    test_user: User,
) -> None:
    """
    Test password reset request.

    Note: In a real application, this would send an email with reset link.

    Verifies that:
    - Password reset can be requested
    - Returns success message
    """
    response = await client.post(
        "/api/v1/auth/forgot-password",
        json={"email": test_user.email},
    )

    assert response.status_code == 200
    data = response.json()
    assert "message" in data


async def test_forgot_password_nonexistent_email(
    client: AsyncClient,
) -> None:
    """
    Test password reset for non-existent email.

    Verifies that:
    - Returns success even for non-existent emails (security best practice)
    - Prevents email enumeration attacks
    """
    response = await client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "nonexistent@example.com"},
    )

    # Should still return 200 to prevent email enumeration
    assert response.status_code == 200


# Note: Testing password reset with token requires implementing
# token generation in the AuthService. Similar to email verification,
# you would need to:
# 1. Generate a reset token
# 2. Store it securely
# 3. Verify it in the reset-password endpoint
# 4. Update the user's password


# ============================================================================
# EDGE CASES & SECURITY TESTS
# ============================================================================


async def test_login_sql_injection_attempt(client: AsyncClient) -> None:
    """
    Test that SQL injection attempts are safely handled.

    Verifies that:
    - SQL injection attempts don't cause errors
    - Returns appropriate error response
    """
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@example.com' OR '1'='1",
            "password": "anything",
        },
    )

    # Should return 401, not a server error
    assert response.status_code in [401, 422]


async def test_register_xss_attempt(
    client: AsyncClient,
    sample_user_data: dict[str, Any],
) -> None:
    """
    Test that XSS attempts in user data are handled safely.

    Verifies that:
    - Script tags and HTML are properly escaped/validated
    - System remains secure against XSS attacks
    """
    sample_user_data["firstname"] = "<script>alert('xss')</script>"

    response = await client.post("/api/v1/auth/register", json=sample_user_data)

    # The request should either succeed (with data escaped) or fail validation
    assert response.status_code in [201, 422]

    if response.status_code == 201:
        data = response.json()
        # The script should be stored as-is (it's escaped when rendered in HTML)
        assert "<script>" in data["firstname"]
