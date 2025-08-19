"""
Synchronous version of AuthService for testing
This wraps async methods to work with sync SQLAlchemy sessions in tests
"""
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User
from app.services.auth import AuthService as AsyncAuthService


class AuthServiceSync:
    """Synchronous wrapper for AuthService to use in tests"""
    
    # Use the same static methods from AuthService for non-async operations
    get_password_hash = AsyncAuthService.get_password_hash
    verify_password = AsyncAuthService.verify_password
    create_access_token = AsyncAuthService.create_access_token
    verify_token = AsyncAuthService.verify_token
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email from database (sync version)"""
        result = db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
        """Get user by ID from database (sync version)"""
        result = db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    @classmethod
    def authenticate_user(cls, db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password (sync version)"""
        user = cls.get_user_by_email(db, email)
        if not user:
            return None
        if not cls.verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        
        # Update login tracking
        from datetime import datetime
        user.login_count = (user.login_count or 0) + 1
        user.last_login_at = datetime.utcnow()
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    @classmethod
    def create_user(cls, db: Session, email: str, password: str, **kwargs) -> User:
        """Create a new user (sync version)"""
        hashed_password = cls.get_password_hash(password)
        user = User(
            email=email,
            hashed_password=hashed_password,
            **kwargs
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user