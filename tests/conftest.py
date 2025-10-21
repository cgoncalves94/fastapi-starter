"""
Shared test fixtures and configuration for pytest.

This file contains fixtures that are automatically available to all test files.
Learn more: https://docs.pytest.org/en/stable/reference/fixtures.html
"""

import asyncio
from collections.abc import AsyncGenerator
from typing import Any

import pytest
from faker import Faker
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel

from app.api.v1.dependencies.database import get_session
from app.core.config import Settings, get_settings
from app.core.security import create_access_token, get_password_hash
from app.main import app
from app.users.models import User

# Initialize Faker for generating test data
fake = Faker()


# ============================================================================
# TEST SETTINGS & DATABASE CONFIGURATION
# ============================================================================


@pytest.fixture
def test_settings() -> Settings:
    """
    Override settings for testing environment.

    Uses the test PostgreSQL database configured in the CI environment
    or falls back to a local test database.
    """
    settings = get_settings()
    # Use test database name (configured via environment variables in CI)
    settings.postgres_db = "fastapi_starter_test"
    return settings


@pytest.fixture
async def test_engine(test_settings: Settings) -> AsyncGenerator[AsyncEngine, None]:
    """
    Create a test database engine.

    This fixture creates a fresh database for each test function,
    ensuring complete isolation between tests. Tables are created
    before each test and dropped after.
    """
    # Create test engine with the test database
    engine = create_async_engine(
        test_settings.database_url,
        echo=False,  # Set to True to see SQL queries
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # Cleanup: Drop all tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(
    test_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database session for each test.

    This fixture provides a clean database session for each test function.
    After the test completes, all changes are rolled back to keep tests isolated.
    """
    # Create a session factory
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()


# ============================================================================
# TEST CLIENT
# ============================================================================


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create an async test client for making API requests.

    This fixture overrides the database dependency to use our test database.
    All API calls made through this client will use the test database session.
    """
    # Override the database dependency
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_db

    # Create the test client
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as test_client:
        yield test_client

    # Clear overrides after test
    app.dependency_overrides.clear()


# ============================================================================
# TEST USER FIXTURES
# ============================================================================


@pytest.fixture
def user_password() -> str:
    """Consistent password for test users."""
    return "TestPassword123!"


@pytest.fixture
async def test_user(
    db_session: AsyncSession,
    user_password: str,
) -> User:
    """
    Create a regular test user.

    This fixture creates a test user in the database that can be used
    across multiple tests. The user is automatically cleaned up after the test.
    """
    user = User(
        email=fake.email(),
        firstname=fake.first_name(),
        lastname=fake.last_name(),
        hashed_password=get_password_hash(user_password),
        is_active=True,
        is_superuser=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_superuser(
    db_session: AsyncSession,
    user_password: str,
) -> User:
    """
    Create a superuser for testing admin functionality.

    Superusers have elevated permissions and can perform admin operations.
    """
    superuser = User(
        email=fake.email(),
        firstname="Admin",
        lastname="User",
        hashed_password=get_password_hash(user_password),
        is_active=True,
        is_superuser=True,
    )
    db_session.add(superuser)
    await db_session.commit()
    await db_session.refresh(superuser)
    return superuser


@pytest.fixture
async def inactive_user(
    db_session: AsyncSession,
    user_password: str,
) -> User:
    """
    Create an inactive user for testing authorization logic.

    Inactive users should not be able to access protected endpoints.
    """
    user = User(
        email=fake.email(),
        firstname=fake.first_name(),
        lastname=fake.last_name(),
        hashed_password=get_password_hash(user_password),
        is_active=False,
        is_superuser=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# ============================================================================
# AUTHENTICATION FIXTURES
# ============================================================================


@pytest.fixture
def user_token(test_user: User) -> str:
    """
    Generate a valid JWT token for the test user.

    Use this token to authenticate requests as a regular user.
    Example:
        headers = {"Authorization": f"Bearer {user_token}"}
        response = await client.get("/api/v1/users/me", headers=headers)
    """
    return create_access_token(subject=test_user.email)


@pytest.fixture
def superuser_token(test_superuser: User) -> str:
    """
    Generate a valid JWT token for the test superuser.

    Use this token to authenticate requests as an admin user.
    """
    return create_access_token(subject=test_superuser.email)


@pytest.fixture
def auth_headers(user_token: str) -> dict[str, str]:
    """
    Create authorization headers for regular user requests.

    Example:
        response = await client.get("/api/v1/users/me", headers=auth_headers)
    """
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def superuser_headers(superuser_token: str) -> dict[str, str]:
    """
    Create authorization headers for superuser requests.

    Example:
        response = await client.get("/api/v1/users", headers=superuser_headers)
    """
    return {"Authorization": f"Bearer {superuser_token}"}


# ============================================================================
# HELPER FIXTURES
# ============================================================================


@pytest.fixture
def sample_user_data(user_password: str) -> dict[str, Any]:
    """
    Generate sample user data for registration/creation tests.

    Returns a dictionary with valid user data that can be used
    in registration or user creation requests.
    """
    return {
        "email": fake.email(),
        "firstname": fake.first_name(),
        "lastname": fake.last_name(),
        "password": user_password,
    }
