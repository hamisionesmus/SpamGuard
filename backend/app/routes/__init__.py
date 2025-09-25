"""
API routes package
"""

from fastapi import APIRouter

from app.routes.auth import router as auth_router
from app.routes.api import router as api_router
from app.routes.admin import router as admin_router

# Main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["authentication"]
)

api_router.include_router(
    api_router,
    prefix="/predict",
    tags=["predictions"]
)

api_router.include_router(
    admin_router,
    prefix="/admin",
    tags=["administration"]
)