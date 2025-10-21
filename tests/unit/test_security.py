"""
Unit tests for security utilities.

These tests verify the core security functions:
- Password hashing and verification
- JWT token creation and validation
- Password reset token generation
- Email verification token generation

These are UNIT tests - they test functions in isolation without
requiring a database or external services.
"""

from datetime import UTC, datetime, timedelta

import pytest

from app.core.security import (
    create_access_token,
    decode_access_token,
    generate_email_verification_token,
    generate_password_reset_token,
    get_password_hash,
    verify_email_verification_token,
    verify_password,
    verify_password_reset_token,
)

# Mark all tests in this file as unit tests
pytestmark = pytest.mark.unit


# ============================================================================
# PASSWORD HASHING TESTS
# ============================================================================


def test_password_hashing() -> None:
    """
    Test that passwords are hashed correctly.

    Verifies that:
    - Password can be hashed
    - Hash is different from original password
    - Hash is a string
    """
    password = "SuperSecretPassword123!"
    hashed = get_password_hash(password)

    assert hashed != password
    assert isinstance(hashed, str)
    assert len(hashed) > 0


def test_password_verification_success() -> None:
    """
    Test successful password verification.

    Verifies that:
    - Correct password matches its hash
    - Returns True for matching password
    """
    password = "MyPassword123!"
    hashed = get_password_hash(password)

    assert verify_password(password, hashed) is True


def test_password_verification_failure() -> None:
    """
    Test password verification with wrong password.

    Verifies that:
    - Wrong password doesn't match hash
    - Returns False for non-matching password
    """
    password = "CorrectPassword123!"
    wrong_password = "WrongPassword456!"
    hashed = get_password_hash(password)

    assert verify_password(wrong_password, hashed) is False


def test_same_password_different_hashes() -> None:
    """
    Test that same password produces different hashes.

    Verifies that:
    - Each hash uses a unique salt
    - Same password hashed twice produces different results
    - Both hashes verify correctly (they're both valid)
    """
    password = "SamePassword123!"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)

    # Hashes should be different (due to different salts)
    assert hash1 != hash2

    # But both should verify the same password
    assert verify_password(password, hash1)
    assert verify_password(password, hash2)


def test_empty_password() -> None:
    """
    Test hashing an empty password.

    Note: In production, you should validate password requirements
    before hashing (minimum length, complexity, etc.)
    """
    password = ""
    hashed = get_password_hash(password)

    assert verify_password(password, hashed)


# ============================================================================
# JWT ACCESS TOKEN TESTS
# ============================================================================


def test_create_access_token() -> None:
    """
    Test creating a JWT access token.

    Verifies that:
    - Token can be created
    - Token is a non-empty string
    """
    data = {"sub": "user@example.com"}
    token = create_access_token(data)

    assert isinstance(token, str)
    assert len(token) > 0


def test_create_and_decode_access_token() -> None:
    """
    Test creating and decoding an access token.

    Verifies that:
    - Data can be encoded into a token
    - Data can be decoded from the token
    - Decoded data matches original data
    """
    data = {"sub": "user@example.com", "role": "user"}
    token = create_access_token(data)

    decoded = decode_access_token(token)

    assert decoded["sub"] == data["sub"]
    assert decoded["role"] == data["role"]
    assert "exp" in decoded  # Expiration should be added automatically


def test_create_token_with_custom_expiration() -> None:
    """
    Test creating a token with custom expiration time.

    Verifies that:
    - Custom expiration delta is respected
    - Expiration time is set correctly
    """
    data = {"sub": "user@example.com"}
    expires_delta = timedelta(minutes=15)
    token = create_access_token(data, expires_delta=expires_delta)

    decoded = decode_access_token(token)

    # Check that expiration is set
    assert "exp" in decoded

    # Verify expiration is approximately 15 minutes from now
    exp_timestamp = decoded["exp"]
    exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=UTC)
    now = datetime.now(UTC)
    delta = exp_datetime - now

    # Should be close to 15 minutes (within 10 seconds tolerance)
    assert 14.8 < delta.total_seconds() / 60 < 15.2


def test_decode_invalid_token() -> None:
    """
    Test decoding an invalid token.

    Verifies that:
    - Invalid tokens raise ValueError
    - Error message indicates validation failure
    """
    invalid_token = "invalid.token.here"

    with pytest.raises(ValueError) as exc_info:
        decode_access_token(invalid_token)

    assert "credentials" in str(exc_info.value).lower()


def test_decode_token_wrong_signature() -> None:
    """
    Test decoding a token with wrong signature.

    Verifies that:
    - Tampered tokens are rejected
    - Raises ValueError
    """
    data = {"sub": "user@example.com"}
    token = create_access_token(data)

    # Tamper with the token (change last character)
    tampered_token = token[:-1] + ("A" if token[-1] != "A" else "B")

    with pytest.raises(ValueError):
        decode_access_token(tampered_token)


# ============================================================================
# PASSWORD RESET TOKEN TESTS
# ============================================================================


def test_generate_password_reset_token() -> None:
    """
    Test generating a password reset token.

    Verifies that:
    - Token can be generated
    - Token is a non-empty string
    """
    email = "user@example.com"
    token = generate_password_reset_token(email)

    assert isinstance(token, str)
    assert len(token) > 0


def test_verify_password_reset_token_success() -> None:
    """
    Test verifying a valid password reset token.

    Verifies that:
    - Valid token returns the email
    - Email matches the one used to generate token
    """
    email = "user@example.com"
    token = generate_password_reset_token(email)

    verified_email = verify_password_reset_token(token)

    assert verified_email == email


def test_verify_password_reset_token_invalid() -> None:
    """
    Test verifying an invalid password reset token.

    Verifies that:
    - Invalid tokens return None
    - No exception is raised
    """
    invalid_token = "invalid.reset.token"

    result = verify_password_reset_token(invalid_token)

    assert result is None


def test_verify_password_reset_token_wrong_type() -> None:
    """
    Test that access tokens can't be used as password reset tokens.

    Verifies that:
    - Token type is validated
    - Access tokens are rejected as password reset tokens
    """
    # Create a regular access token
    data = {"sub": "user@example.com"}
    access_token = create_access_token(data)

    # Try to use it as a password reset token
    result = verify_password_reset_token(access_token)

    # Should return None because it's not a password reset token
    assert result is None


# ============================================================================
# EMAIL VERIFICATION TOKEN TESTS
# ============================================================================


def test_generate_email_verification_token() -> None:
    """
    Test generating an email verification token.

    Verifies that:
    - Token can be generated
    - Token is a non-empty string
    """
    email = "user@example.com"
    token = generate_email_verification_token(email)

    assert isinstance(token, str)
    assert len(token) > 0


def test_verify_email_verification_token_success() -> None:
    """
    Test verifying a valid email verification token.

    Verifies that:
    - Valid token returns the email
    - Email matches the one used to generate token
    """
    email = "user@example.com"
    token = generate_email_verification_token(email)

    verified_email = verify_email_verification_token(token)

    assert verified_email == email


def test_verify_email_verification_token_invalid() -> None:
    """
    Test verifying an invalid email verification token.

    Verifies that:
    - Invalid tokens return None
    - No exception is raised
    """
    invalid_token = "invalid.verification.token"

    result = verify_email_verification_token(invalid_token)

    assert result is None


def test_verify_email_verification_token_wrong_type() -> None:
    """
    Test that password reset tokens can't be used as email verification tokens.

    Verifies that:
    - Token type is validated
    - Password reset tokens are rejected
    """
    # Create a password reset token
    email = "user@example.com"
    reset_token = generate_password_reset_token(email)

    # Try to use it as an email verification token
    result = verify_email_verification_token(reset_token)

    # Should return None because it's not an email verification token
    assert result is None


def test_different_token_types_are_distinct() -> None:
    """
    Test that different token types are properly distinguished.

    Verifies that:
    - Each token type is unique
    - Tokens can't be interchanged
    """
    email = "user@example.com"

    access_token = create_access_token({"sub": email})
    reset_token = generate_password_reset_token(email)
    verify_token = generate_email_verification_token(email)

    # All tokens should be different
    assert access_token != reset_token
    assert access_token != verify_token
    assert reset_token != verify_token

    # Reset token should only work for password reset
    assert verify_password_reset_token(reset_token) == email
    assert verify_email_verification_token(reset_token) is None

    # Verify token should only work for email verification
    assert verify_email_verification_token(verify_token) == email
    assert verify_password_reset_token(verify_token) is None


# ============================================================================
# EDGE CASES & SECURITY TESTS
# ============================================================================


def test_password_with_special_characters() -> None:
    """
    Test password hashing with special characters.

    Verifies that:
    - Special characters are handled correctly
    - Unicode characters work properly
    """
    passwords = [
        "Pass@word!123",
        "пароль123",  # Cyrillic
        "密码123",  # Chinese
        "contraseña123",  # Spanish
        "P@$$w0rd!@#$%^&*()",
    ]

    for password in passwords:
        hashed = get_password_hash(password)
        assert verify_password(password, hashed)


def test_very_long_password() -> None:
    """
    Test bcrypt's password length limitation.

    Bcrypt has a maximum password length of 72 bytes. This test
    documents this limitation and verifies it raises an appropriate error.

    Note: In production, you might want to pre-hash long passwords
    before passing them to bcrypt (e.g., using SHA256).
    """
    # Passwords up to 72 bytes should work fine
    password_72_bytes = "a" * 72
    hashed = get_password_hash(password_72_bytes)
    assert verify_password(password_72_bytes, hashed)

    # Passwords longer than 72 bytes raise ValueError
    password_too_long = "a" * 1000
    with pytest.raises(ValueError) as exc_info:
        get_password_hash(password_too_long)

    assert "72 bytes" in str(exc_info.value)


def test_token_expiration_values() -> None:
    """
    Test that token expiration is set correctly.

    Verifies that:
    - Password reset tokens expire in 24 hours
    - Email verification tokens expire in 72 hours
    """
    import jwt

    from app.core.config import get_settings

    settings = get_settings()
    email = "user@example.com"

    # Check password reset token (24 hours)
    reset_token = generate_password_reset_token(email)
    reset_payload = jwt.decode(
        reset_token, settings.secret_key, algorithms=[settings.algorithm]
    )
    reset_exp = datetime.fromtimestamp(reset_payload["exp"], tz=UTC)
    reset_delta = reset_exp - datetime.now(UTC)
    # Should be approximately 24 hours
    assert 23.9 < reset_delta.total_seconds() / 3600 < 24.1

    # Check email verification token (72 hours)
    verify_token = generate_email_verification_token(email)
    verify_payload = jwt.decode(
        verify_token, settings.secret_key, algorithms=[settings.algorithm]
    )
    verify_exp = datetime.fromtimestamp(verify_payload["exp"], tz=UTC)
    verify_delta = verify_exp - datetime.now(UTC)
    # Should be approximately 72 hours
    assert 71.9 < verify_delta.total_seconds() / 3600 < 72.1
