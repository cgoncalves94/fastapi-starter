"""
Authentication routes for API v1.
"""

from fastapi import APIRouter, status

from app.api.v1.dependencies.authentication import CurrentUser
from app.api.v1.dependencies.services import AuthServiceDep, UserServiceDep
from app.auth.schemas import (
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    ResetPasswordRequest,
    SendEmailVerificationRequest,
    Token,
    VerifyEmailRequest,
)
from app.users.schemas import UserResponse, UserResponseComplete

router = APIRouter(prefix="/auth", tags=["v1 - Authentication"])


# ================================
# REGISTRATION & LOGIN
# ================================


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


# ================================
# USER INFORMATION
# ================================


@router.get("/me", response_model=UserResponseComplete)
async def get_current_user_info(
    current_user: CurrentUser,
    user_service: UserServiceDep,
) -> UserResponseComplete:
    """Get current user information with lightweight workspace IDs."""
    return await user_service.get_user_complete(current_user.id)


# ================================
# EMAIL VERIFICATION
# ================================


@router.post("/send-email-verification", response_model=MessageResponse)
async def send_email_verification(
    request: SendEmailVerificationRequest,
    auth_service: AuthServiceDep,
) -> MessageResponse:
    """Send an email verification token to the user's email."""
    await auth_service.send_email_verification(request.email)
    return MessageResponse(
        message="If a user with that email exists and is not verified, a verification email has been sent."
    )


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    request: VerifyEmailRequest,
    auth_service: AuthServiceDep,
) -> MessageResponse:
    """Verify user's email using a token."""
    await auth_service.verify_email(request.token)
    return MessageResponse(message="Email verified successfully.")


# ================================
# PASSWORD RESET
# ================================


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    auth_service: AuthServiceDep,
) -> MessageResponse:
    """Request a password reset token."""
    await auth_service.forgot_password(request.email)
    return MessageResponse(
        message="If a user with that email exists, a password reset email has been sent."
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    request: ResetPasswordRequest,
    auth_service: AuthServiceDep,
) -> MessageResponse:
    """Reset user's password using a token."""
    await auth_service.reset_password(
        request.token, request.new_password.get_secret_value()
    )
    return MessageResponse(message="Password has been reset successfully.")
