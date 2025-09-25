"""
Admin routes for system management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from app.database import get_db
from app.services.auth import get_current_admin_user
from app.services.admin import AdminService
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/users")
async def list_users(
    limit: int = 50,
    offset: int = 0,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """List all users (admin only)"""
    try:
        admin_service = AdminService(db)
        users = await admin_service.list_users(limit=limit, offset=offset)
        return {"users": users}
    except Exception as e:
        logger.error(f"Failed to list users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )


@router.get("/stats")
async def system_stats(
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get system statistics"""
    try:
        admin_service = AdminService(db)
        stats = await admin_service.get_system_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to get system stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system statistics"
        )


@router.post("/models/retrain")
async def retrain_model(
    model_version: str = "latest",
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Trigger model retraining (admin only)"""
    try:
        admin_service = AdminService(db)
        job_id = await admin_service.trigger_model_retraining(model_version)
        return {"job_id": job_id, "status": "started"}
    except Exception as e:
        logger.error(f"Failed to trigger model retraining: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start model retraining"
        )


@router.get("/jobs/{job_id}")
async def get_job_status(
    job_id: str,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get background job status"""
    try:
        admin_service = AdminService(db)
        job_status = await admin_service.get_job_status(job_id)
        return job_status
    except Exception as e:
        logger.error(f"Failed to get job status: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )