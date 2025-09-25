"""
GraphQL API endpoints using Strawberry
"""

import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry import Info
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.database import get_db
from app.services.ml import MLService
from app.services.auth import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)


@strawberry.type
class PredictionResult:
    prediction: str
    confidence: float
    explanation: Optional[dict] = None
    model_version: str


@strawberry.type
class ModelInfo:
    name: str
    version: str
    algorithm: str
    metrics: Optional[dict] = None
    training_samples: int
    created: float


@strawberry.type
class UserInfo:
    id: str
    email: str
    full_name: str
    is_active: bool


@strawberry.input
class PredictionInput:
    text: str
    model_version: Optional[str] = "latest"


@strawberry.type
class Query:
    @strawberry.field
    async def predict(
        self,
        info: Info,
        input: PredictionInput,
        current_user: User = strawberry.field(resolver=lambda: get_current_user)
    ) -> PredictionResult:
        """Make a prediction"""
        db = info.context["db"]
        ml_service = MLService()

        result = await ml_service.predict(
            text=input.text,
            model_version=input.model_version,
            user_id=str(current_user.id),
            db=db
        )

        return PredictionResult(
            prediction=result["prediction"],
            confidence=result["confidence"],
            explanation=result.get("explanation"),
            model_version=result["model_version"]
        )

    @strawberry.field
    async def models(
        self,
        info: Info,
        current_user: User = strawberry.field(resolver=lambda: get_current_user)
    ) -> List[ModelInfo]:
        """List available models"""
        ml_service = MLService()
        models = await ml_service.list_models()

        return [
            ModelInfo(
                name=model["name"],
                version=model.get("version", "1.0"),
                algorithm=model.get("algorithm", "unknown"),
                metrics=model.get("metrics"),
                training_samples=model.get("training_samples", 0),
                created=model["created"]
            )
            for model in models
        ]

    @strawberry.field
    async def me(
        self,
        info: Info,
        current_user: User = strawberry.field(resolver=lambda: get_current_user)
    ) -> UserInfo:
        """Get current user info"""
        return UserInfo(
            id=str(current_user.id),
            email=current_user.email,
            full_name=current_user.full_name,
            is_active=current_user.is_active
        )


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def predict(
        self,
        info: Info,
        input: PredictionInput,
        current_user: User = strawberry.field(resolver=lambda: get_current_user)
    ) -> PredictionResult:
        """Make a prediction (mutation for consistency)"""
        # Reuse the query logic
        return await Query.predict(self, info, input, current_user)


# Create GraphQL schema
schema = strawberry.Schema(query=Query, mutation=Mutation)

# Create GraphQL router
graphql_app = GraphQLRouter(
    schema,
    context_getter=lambda: {"db": get_db}
)