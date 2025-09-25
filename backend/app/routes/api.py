"""
Prediction API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import logging

from app.database import get_db
from app.services.auth import get_current_user
from app.services.ml import MLService
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()


class PredictionRequest(BaseModel):
    text: str
    model_version: str = "latest"


class PredictionResponse(BaseModel):
    prediction: str
    confidence: float
    explanation: dict = None
    model_version: str


@router.post("/", response_model=PredictionResponse)
async def predict(
    request: PredictionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Make a spam/fraud prediction"""
    try:
        ml_service = MLService()
        result = await ml_service.predict(
            text=request.text,
            model_version=request.model_version,
            user_id=current_user.id,
            db=db
        )

        return PredictionResponse(
            prediction=result["prediction"],
            confidence=result["confidence"],
            explanation=result.get("explanation"),
            model_version=result["model_version"]
        )

    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Prediction failed"
        )


@router.get("/models")
async def list_models(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List available models"""
    try:
        ml_service = MLService()
        models = await ml_service.list_models()
        return {"models": models}
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve models"
        )


@router.get("/history")
async def prediction_history(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's prediction history"""
    try:
        ml_service = MLService()
        history = await ml_service.get_prediction_history(
            user_id=current_user.id,
            limit=limit,
            offset=offset,
            db=db
        )
        return {"history": history}
    except Exception as e:
        logger.error(f"Failed to get prediction history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve prediction history"
        )