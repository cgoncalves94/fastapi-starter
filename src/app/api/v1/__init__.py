"""
API v1 router aggregation.
"""

from fastapi import APIRouter

from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.users import router as users_router
from app.api.v1.routers.workspaces import router as workspaces_router

api_router = APIRouter()

# Include all v1 routers
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(workspaces_router)
