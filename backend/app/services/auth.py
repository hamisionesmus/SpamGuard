"""
Authentication service
"""

import jwt
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import logging

from app.config import settings
from app.models.user import User, Role
from app.schemas.auth import UserCreate, UserResponse, Token, TokenData
from app.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication service"""

    def __init__(self, db: AsyncSession):
        self.db = db

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        query = select(User).where(User.email == email, User.is_active == True)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        query = select(User).where(User.id == user_id, User.is_active == True)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user"""
        # Check if user already exists
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError("User with this email already exists")

        # Get default role
        query = select(Role).where(Role.name == "free")
        result = await self.db.execute(query)
        default_role = result.scalar_one_or_none()

        if not default_role:
            # Create default role if it doesn't exist
            default_role = Role(
                name="free",
                description="Free tier user",
                permissions='{"read": true, "predict": true}'
            )
            self.db.add(default_role)
            await self.db.commit()
            await self.db.refresh(default_role)

        # Create user
        hashed_password = self.get_password_hash(user_data.password)
        user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role_id=default_role.id
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return UserResponse.from_orm(user)

    async def authenticate_user(self, email: str, password: str) -> Token:
        """Authenticate user and return tokens"""
        user = await self.get_user_by_email(email)
        if not user:
            raise ValueError("Invalid credentials")

        if not self.verify_password(password, user.hashed_password):
            raise ValueError("Invalid credentials")

        # Generate tokens
        access_token = self.create_access_token({"sub": str(user.id), "email": user.email})
        refresh_token = self.create_refresh_token({"sub": str(user.id)})

        return Token(
            access_token=access_token,
            refresh_token=refresh_token
        )

    def create_access_token(self, data: dict) -> str:
        """Create access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, data: dict) -> str:
        """Create refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email: str = payload.get("email")
            user_id: str = payload.get("sub")
            token_type: str = payload.get("type")

            if user_id is None:
                return None

            return TokenData(email=email, user_id=user_id)
        except jwt.PyJWTError:
            return None

    async def refresh_access_token(self, refresh_token: str) -> Token:
        """Refresh access token using refresh token"""
        token_data = self.verify_token(refresh_token)
        if not token_data or not token_data.user_id:
            raise ValueError("Invalid refresh token")

        user = await self.get_user_by_id(token_data.user_id)
        if not user:
            raise ValueError("User not found")

        # Generate new tokens
        access_token = self.create_access_token({"sub": str(user.id), "email": user.email})
        new_refresh_token = self.create_refresh_token({"sub": str(user.id)})

        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token
        )

    async def logout_user(self, token: str):
        """Logout user (invalidate token)"""
        # In a production system, you might want to add tokens to a blacklist
        # For now, we'll just log the logout
        token_data = self.verify_token(token)
        if token_data and token_data.user_id:
            logger.info(f"User {token_data.user_id} logged out")


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    """Dependency to get current user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    auth_service = AuthService(db)
    token_data = auth_service.verify_token(token)
    if not token_data:
        raise credentials_exception

    user = await auth_service.get_user_by_id(token_data.user_id)
    if not user:
        raise credentials_exception

    return user


async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to get current admin user"""
    if not current_user.role or current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user