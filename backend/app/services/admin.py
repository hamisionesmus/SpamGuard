"""
Admin service for system management
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Dict, Any
import logging

from app.models.user import User
from app.models.prediction import Prediction, Dataset, TrainingJob, Model

logger = logging.getLogger(__name__)


class AdminService:
    """Admin service for system management"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_users(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """List all users"""
        query = select(User).limit(limit).offset(offset)
        result = await self.db.execute(query)
        users = result.scalars().all()

        return [
            {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "role": user.role.name if user.role else None
            }
            for user in users
        ]

    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        # User stats
        user_query = select(func.count(User.id))
        user_result = await self.db.execute(user_query)
        total_users = user_result.scalar()

        # Prediction stats
        pred_query = select(func.count(Prediction.id))
        pred_result = await self.db.execute(pred_query)
        total_predictions = pred_result.scalar()

        # Dataset stats
        dataset_query = select(func.count(Dataset.id))
        dataset_result = await self.db.execute(dataset_query)
        total_datasets = dataset_result.scalar()

        # Model stats
        model_query = select(func.count(Model.id))
        model_result = await self.db.execute(model_query)
        total_models = model_result.scalar()

        # Recent predictions (last 24 hours)
        from datetime import datetime, timedelta
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_pred_query = select(func.count(Prediction.id)).where(Prediction.created_at >= yesterday)
        recent_pred_result = await self.db.execute(recent_pred_query)
        recent_predictions = recent_pred_result.scalar()

        return {
            "total_users": total_users,
            "total_predictions": total_predictions,
            "total_datasets": total_datasets,
            "total_models": total_models,
            "recent_predictions_24h": recent_predictions,
            "timestamp": datetime.utcnow()
        }

    async def trigger_model_retraining(self, model_version: str = "latest") -> str:
        """Trigger model retraining job"""
        # This would typically queue a background job
        # For now, return a mock job ID
        import uuid
        job_id = str(uuid.uuid4())

        logger.info(f"Triggered model retraining job {job_id} for version {model_version}")

        # TODO: Implement actual background job queuing
        # This could use Celery, RQ, or similar

        return job_id

    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get background job status"""
        # TODO: Implement actual job status checking
        # For now, return mock status
        return {
            "job_id": job_id,
            "status": "completed",
            "progress": 100,
            "message": "Model retraining completed successfully"
        }