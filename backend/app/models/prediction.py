"""
Prediction database models
"""

from sqlalchemy import Column, String, Text, Float, DateTime, UUID, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Prediction(Base):
    """Prediction model"""
    __tablename__ = "predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    model_id = Column(UUID(as_uuid=True), ForeignKey("models.id"), nullable=False, index=True)
    input_text = Column(Text, nullable=False)
    prediction = Column(String(20), nullable=False)  # spam/ham/fraud/legitimate
    confidence = Column(Float)
    explanation = Column(String)  # JSON string
    source = Column(String(50), default="api")  # api/web/webhook
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    user = relationship("User", back_populates="predictions")
    model = relationship("Model", back_populates="predictions")
    logs = relationship("PredictionLog", back_populates="prediction")


class PredictionLog(Base):
    """Prediction log model for detailed tracking"""
    __tablename__ = "prediction_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prediction_id = Column(UUID(as_uuid=True), ForeignKey("predictions.id"), nullable=False)
    level = Column(String(20), default="info")  # info/warning/error
    message = Column(Text, nullable=False)
    metadata = Column(String)  # JSON string
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    prediction = relationship("Prediction", back_populates="logs")


class Model(Base):
    """ML model metadata"""
    __tablename__ = "models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    version = Column(String(50), nullable=False)
    algorithm = Column(String(100), nullable=False)
    file_path = Column(String(500), nullable=False)
    metadata = Column(String)  # JSON string with metrics
    is_active = Column(String(10), default="false")  # true/false string for compatibility
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    predictions = relationship("Prediction", back_populates="model")
    training_jobs = relationship("TrainingJob", back_populates="model")


class Dataset(Base):
    """Training dataset model"""
    __tablename__ = "datasets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    file_path = Column(String(500), nullable=False)
    record_count = Column(Integer)
    schema = Column(String)  # JSON string
    status = Column(String(20), default="uploaded")  # uploaded/processing/processed/failed
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="datasets")
    training_jobs = relationship("TrainingJob", back_populates="dataset")


class TrainingJob(Base):
    """Model training job model"""
    __tablename__ = "training_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"))
    model_id = Column(UUID(as_uuid=True), ForeignKey("models.id"))
    status = Column(String(20), default="pending")  # pending/running/completed/failed
    config = Column(String)  # JSON string
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    logs = Column(Text)

    # Relationships
    dataset = relationship("Dataset", back_populates="training_jobs")
    model = relationship("Model", back_populates="training_jobs")