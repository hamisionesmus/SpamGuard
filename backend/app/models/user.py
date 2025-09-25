"""
User database models
"""

from sqlalchemy import Column, String, Boolean, DateTime, UUID, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"))

    # Relationships
    role = relationship("Role", back_populates="users")
    predictions = relationship("Prediction", back_populates="user")
    api_keys = relationship("APIKey", back_populates="user")
    datasets = relationship("Dataset", back_populates="user")


class Role(Base):
    """User role model"""
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(500))
    permissions = Column(String, nullable=False, default="{}")  # JSON string

    # Relationships
    users = relationship("User", back_populates="role")


class APIKey(Base):
    """API key model"""
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    key_hash = Column(String(255), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    rate_limit = Column(String(50), default=1000)  # requests per hour
    tier = Column(String(20), default="free")

    # Relationships
    user = relationship("User", back_populates="api_keys")