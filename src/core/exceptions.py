"""
Custom exception classes for the application.
"""


# ===========================================
# DOMAIN/BUSINESS EXCEPTIONS (for Service Layer)
# ===========================================


class DomainException(Exception):
    """Base domain exception."""

    pass


class NotFoundError(DomainException):
    """Entity not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message)


class ConflictError(DomainException):
    """Resource conflict (duplicate, constraint violation)."""

    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message)


class ValidationError(DomainException):
    """Business rule or validation error."""

    def __init__(self, message: str = "Validation failed"):
        super().__init__(message)


class PermissionDeniedError(DomainException):
    """Insufficient permissions."""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(message)
