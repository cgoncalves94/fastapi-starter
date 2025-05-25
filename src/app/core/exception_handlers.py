"""
Global exception handlers for FastAPI application.
Translates domain exceptions to appropriate HTTP responses.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import (
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)


async def domain_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Handle domain exceptions and convert them to HTTP responses."""

    # Map domain exceptions to HTTP status codes
    if isinstance(exc, NotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    elif isinstance(exc, ConflictError):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    elif isinstance(exc, ValidationError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    elif isinstance(exc, PermissionDeniedError):
        return JSONResponse(status_code=403, content={"detail": str(exc)})

    # Fallback for unknown domain exceptions
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


async def sqlalchemy_exception_handler(
    _request: Request, exc: Exception
) -> JSONResponse:
    """Handle SQLAlchemy exceptions without exposing internal details."""
    if isinstance(exc, IntegrityError):
        return JSONResponse(
            status_code=400,
            content={"detail": "Operation failed due to data constraints"},
        )

    # For other SQLAlchemy errors, return generic message
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


async def unhandled_exception_handler(
    _request: Request, _exc: Exception
) -> JSONResponse:
    """Safety net for unhandled exceptions."""
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
