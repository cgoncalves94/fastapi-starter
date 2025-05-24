"""
Authentication routes.
"""

from fastapi import APIRouter, status

from api.v1.dependencies.authentication import CurrentUser
from src.api.v1.dependencies.services import AuthServiceDep
from src.api.v1.schemas.auth import LoginRequest, RegisterRequest, Token
from src.api.v1.schemas.user import UserResponse

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


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: CurrentUser) -> UserResponse:
    """Get current user information."""
    return UserResponse.model_validate(current_user)
