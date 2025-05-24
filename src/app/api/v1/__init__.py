"""
API v1 router aggregation.
"""

from fastapi import APIRouter

from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.workspaces.router import router as workspaces_router

api_router = APIRouter()

# Include all domain routers
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(workspaces_router)
