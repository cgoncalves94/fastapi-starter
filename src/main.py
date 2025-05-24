"""
FastAPI application main entry point.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.routers import auth, users, workspaces
from src.core.config import get_settings
from src.core.database import init_db
from src.core.exceptions import DomainException
from src.core.exception_handlers import (
    domain_exception_handler,
    unhandled_exception_handler,
)

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifespan events."""
    # Initialize database
    await init_db()
    yield


# Metadata for OpenAPI tags
tags_metadata = [
    {
        "name": "v1 - Authentication",
        "description": "API v1 - User authentication, registration, and current user information.",
    },
    {
        "name": "v1 - Users",
        "description": "API v1 - User management operations. Access restricted by roles.",
    },
    {
        "name": "v1 - Workspaces",
        "description": "API v1 - Workspace management operations.",
    },
    {
        "name": "v1 - Workspace Members",
        "description": "API v1 - Operations for managing members within a workspace.",
    },
]

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
    openapi_tags=tags_metadata,
)

# Register exception handlers
app.add_exception_handler(DomainException, domain_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Include routers
app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(users.router, prefix=settings.api_v1_prefix)
app.include_router(workspaces.router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.app_version}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
