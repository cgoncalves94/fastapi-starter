"""
Authentication routes.
"""

from fastapi import APIRouter, status

from app.api.v1.dependencies.authentication import CurrentUser
from app.api.v1.dependencies.services import AuthServiceDep, UserServiceDep
from app.auth.schemas import LoginRequest, RegisterRequest, Token
from app.users.schemas import UserResponse, UserResponseComplete

router = APIRouter(prefix="/auth", tags=["v1 - Authentication"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    user_data: RegisterRequest,
    auth_service: AuthServiceDep,
) -> UserResponse:
    """Register a new user."""
    return await auth_service.register(user_data)


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    auth_service: AuthServiceDep,
) -> Token:
    """Login user and return access token."""
    return await auth_service.login(login_data)


@router.get("/me", response_model=UserResponseComplete)
async def get_current_user_info(
    current_user: CurrentUser,
    user_service: UserServiceDep,
) -> UserResponseComplete:
    """Get current user information with lightweight workspace IDs."""
    return await user_service.get_user_complete(current_user.id)
