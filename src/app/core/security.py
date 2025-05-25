"""
Security utilities for authentication and password handling.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt
from jwt import PyJWTError
from pydantic import EmailStr

from .config import get_settings

settings = get_settings()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode a JWT access token."""
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except jwt.ExpiredSignatureError as exc:
        raise ValueError("Token has expired") from exc
    except PyJWTError as exc:
        raise ValueError("Could not validate credentials") from exc


def generate_password_reset_token(email: EmailStr) -> str:
    """Generate a password reset token for the given email."""
    delta = timedelta(hours=24)  # 24 hours expiry
    now = datetime.now(UTC)
    expires = now + delta
    exp = expires.timestamp()

    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email, "type": "password_reset"},
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> EmailStr | None:
    """Verify a password reset token and return the email if valid."""
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        # Check if it's a password reset token
        if payload.get("type") != "password_reset":
            return None
        return payload["sub"]
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError):
        return None


def generate_email_verification_token(email: EmailStr) -> str:
    """Generate an email verification token for the given email."""
    delta = timedelta(hours=72)  # 72 hours expiry
    now = datetime.now(UTC)
    expires = now + delta
    exp = expires.timestamp()

    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email, "type": "email_verification"},
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    return encoded_jwt


def verify_email_verification_token(token: str) -> EmailStr | None:
    """Verify an email verification token and return the email if valid."""
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        # Check if it's an email verification token
        if payload.get("type") != "email_verification":
            return None
        return payload["sub"]
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError):
        return None
