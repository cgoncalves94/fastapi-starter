"""
Unit tests for UserService.

These tests demonstrate how to test service layer business logic.
In a full test suite, you might mock the repository layer, but for
a learning-focused starter project, we'll test with a real test database
to keep things simple and clear.

Note: These tests use the database fixtures from conftest.py,
making them more like "service integration tests". For pure unit tests,
you would mock the UserRepository. This approach is chosen for
educational clarity.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.core.security import get_password_hash, verify_password
from app.users.models import User
from app.users.repository import UserRepository
from app.users.schemas import UserCreate, UserUpdate
from app.users.service import UserService

# Mark all tests in this file as unit tests
pytestmark = pytest.mark.unit


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
async def user_repository(db_session: AsyncSession) -> UserRepository:
    """Create a UserRepository instance for testing."""
    return UserRepository(db_session)


@pytest.fixture
async def user_service(user_repository: UserRepository) -> UserService:
    """Create a UserService instance for testing."""
    return UserService(user_repository)


# ============================================================================
# USER CREATION TESTS
# ============================================================================


async def test_create_user_success(
    user_service: UserService,
    user_password: str,
) -> None:
    """
    Test creating a new user through the service.

    Verifies that:
    - User can be created with valid data
    - Password is hashed (not stored in plain text)
    - User is marked as active by default
    """
    user_data = UserCreate(
        email="newuser@example.com",
        firstname="New",
        lastname="User",
        password=user_password,
    )

    created_user = await user_service.create_user(user_data)

    assert created_user.email == user_data.email
    assert created_user.firstname == user_data.firstname
    assert created_user.lastname == user_data.lastname
    assert created_user.is_active is True
    assert created_user.is_superuser is False

    # Password should be hashed, not plain text
    assert created_user.hashed_password != user_password
    assert verify_password(user_password, created_user.hashed_password)


async def test_create_user_duplicate_email(
    user_service: UserService,
    test_user: User,
    user_password: str,
) -> None:
    """
    Test that creating a user with duplicate email fails.

    Verifies that:
    - Duplicate email raises ConflictError
    - Error message indicates the conflict
    """
    user_data = UserCreate(
        email=test_user.email,  # Use existing user's email
        firstname="Duplicate",
        lastname="User",
        password=user_password,
    )

    with pytest.raises(ConflictError) as exc_info:
        await user_service.create_user(user_data)

    assert "already registered" in str(exc_info.value).lower()


# ============================================================================
# GET USER TESTS
# ============================================================================


async def test_get_user_by_id_success(
    user_service: UserService,
    test_user: User,
) -> None:
    """
    Test retrieving a user by ID.

    Verifies that:
    - User can be retrieved by ID
    - Returned data matches the user
    """
    retrieved_user = await user_service.get_user_by_id(test_user.id)

    assert retrieved_user.id == test_user.id
    assert retrieved_user.email == test_user.email


async def test_get_user_by_id_not_found(user_service: UserService) -> None:
    """
    Test retrieving a non-existent user.

    Verifies that:
    - NotFoundError is raised for non-existent user
    """
    from uuid import uuid4

    fake_id = uuid4()

    with pytest.raises(NotFoundError):
        await user_service.get_user_by_id(fake_id)


# ============================================================================
# UPDATE USER TESTS
# ============================================================================


async def test_update_user_success(
    user_service: UserService,
    test_user: User,
) -> None:
    """
    Test updating user information.

    Verifies that:
    - User fields can be updated
    - Only specified fields are changed
    - Returns updated user data
    """
    update_data = UserUpdate(
        firstname="Updated",
        lastname="Name",
    )

    updated_user = await user_service.update_user(test_user.id, update_data)

    assert updated_user.firstname == "Updated"
    assert updated_user.lastname == "Name"
    assert updated_user.email == test_user.email  # Email unchanged


async def test_update_user_partial(
    user_service: UserService,
    test_user: User,
) -> None:
    """
    Test partial update (only one field).

    Verifies that:
    - Can update just one field
    - Other fields remain unchanged
    """
    original_lastname = test_user.lastname

    update_data = UserUpdate(firstname="OnlyFirst")

    updated_user = await user_service.update_user(test_user.id, update_data)

    assert updated_user.firstname == "OnlyFirst"
    assert updated_user.lastname == original_lastname


async def test_update_user_not_found(user_service: UserService) -> None:
    """
    Test updating a non-existent user.

    Verifies that:
    - NotFoundError is raised
    """
    from uuid import uuid4

    fake_id = uuid4()
    update_data = UserUpdate(firstname="Ghost")

    with pytest.raises(NotFoundError):
        await user_service.update_user(fake_id, update_data)


# ============================================================================
# DEACTIVATE USER TESTS
# ============================================================================


async def test_deactivate_user(
    user_service: UserService,
    test_user: User,
) -> None:
    """
    Test deactivating a user.

    Verifies that:
    - User can be deactivated
    - is_active flag is set to False
    """
    deactivated_user = await user_service.deactivate_user(test_user.id)

    assert deactivated_user.is_active is False
    assert deactivated_user.id == test_user.id


async def test_deactivate_already_inactive_user(
    user_service: UserService,
    inactive_user: User,
) -> None:
    """
    Test deactivating an already inactive user.

    Verifies that:
    - No error is raised
    - User remains inactive
    """
    deactivated_user = await user_service.deactivate_user(inactive_user.id)

    assert deactivated_user.is_active is False


# ============================================================================
# DELETE USER TESTS
# ============================================================================


async def test_delete_user(
    user_service: UserService,
    test_user: User,
) -> None:
    """
    Test deleting a user.

    Verifies that:
    - User can be deleted
    - User no longer exists after deletion
    """
    await user_service.delete_user(test_user.id)

    # Verify user is deleted
    with pytest.raises(NotFoundError):
        await user_service.get_user_by_id(test_user.id)


async def test_delete_user_not_found(user_service: UserService) -> None:
    """
    Test deleting a non-existent user.

    Verifies that:
    - NotFoundError is raised
    """
    from uuid import uuid4

    fake_id = uuid4()

    with pytest.raises(NotFoundError):
        await user_service.delete_user(fake_id)


# ============================================================================
# PAGINATION TESTS
# ============================================================================


async def test_get_users_paginated(
    user_service: UserService,
    test_user: User,
    test_superuser: User,
) -> None:
    """
    Test getting paginated list of users.

    Verifies that:
    - Returns paginated response
    - Contains correct metadata
    - Includes users in results
    """
    from app.core.common import PaginationParams

    pagination = PaginationParams(page=1, size=10)
    result = await user_service.get_users_paginated(pagination)

    assert result.total >= 2  # At least test_user and test_superuser
    assert result.page == 1
    assert result.size == 10
    assert len(result.items) >= 2


async def test_get_users_paginated_second_page(
    user_service: UserService,
    test_user: User,
    test_superuser: User,
) -> None:
    """
    Test pagination with different page numbers.

    Verifies that:
    - Different pages return different results
    - Page metadata is correct
    """
    from app.core.common import PaginationParams

    # Get first page with size 1
    page1 = await user_service.get_users_paginated(PaginationParams(page=1, size=1))
    assert len(page1.items) == 1
    assert page1.page == 1

    # Get second page with size 1
    page2 = await user_service.get_users_paginated(PaginationParams(page=2, size=1))
    assert len(page2.items) <= 1  # Might be 0 or 1 depending on total users
    assert page2.page == 2

    # If both pages have items, they should be different users
    if len(page2.items) == 1:
        assert page1.items[0].id != page2.items[0].id


# ============================================================================
# BUSINESS LOGIC TESTS
# ============================================================================


async def test_user_password_is_hashed(
    user_service: UserService,
    user_password: str,
) -> None:
    """
    Test that passwords are always hashed.

    Verifies that:
    - Passwords are never stored in plain text
    - Hashed password can verify original password
    """
    user_data = UserCreate(
        email="secure@example.com",
        firstname="Secure",
        lastname="User",
        password=user_password,
    )

    created_user = await user_service.create_user(user_data)

    # Password should not be stored in plain text
    assert created_user.hashed_password != user_password

    # But should verify correctly
    assert verify_password(user_password, created_user.hashed_password)


async def test_new_users_are_active_by_default(
    user_service: UserService,
    user_password: str,
) -> None:
    """
    Test that newly created users are active by default.

    Verifies that:
    - is_active is True for new users
    - is_superuser is False for new users (unless explicitly set)
    """
    user_data = UserCreate(
        email="newactive@example.com",
        firstname="Active",
        lastname="User",
        password=user_password,
    )

    created_user = await user_service.create_user(user_data)

    assert created_user.is_active is True
    assert created_user.is_superuser is False


# ============================================================================
# EDGE CASES
# ============================================================================


async def test_email_case_sensitivity(
    user_service: UserService,
    user_password: str,
) -> None:
    """
    Test email handling with different cases.

    Current behavior: PostgreSQL treats emails as case-sensitive by default.
    This means test@example.com and TEST@EXAMPLE.COM are considered different.

    Note: In production, you might want to add a constraint or normalize emails
    to lowercase before storing to ensure case-insensitive uniqueness.
    """
    user_data1 = UserCreate(
        email="test@example.com",
        firstname="Lower",
        lastname="Case",
        password=user_password,
    )

    created_user1 = await user_service.create_user(user_data1)

    # Try to create user with same email but different case
    user_data2 = UserCreate(
        email="TEST@EXAMPLE.COM",
        firstname="Upper",
        lastname="Case",
        password=user_password,
    )

    # Current implementation: emails are case-sensitive, so this succeeds
    created_user2 = await user_service.create_user(user_data2)

    # Both users should be created successfully
    assert created_user1.email == "test@example.com"
    assert created_user2.email == "TEST@EXAMPLE.COM"
