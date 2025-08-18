from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from uuid import uuid4
from app.db.database import Base

class User(Base):
    __tablename__ = "users"
    
    # Primary key using UUID
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    
    # User authentication fields
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # User profile fields
    username = Column(String(100), unique=True, index=True, nullable=True)
    full_name = Column(String(255), nullable=True)
    
    # User status and permissions
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Password recovery
    password_reset_token = Column(String(255), nullable=True, index=True)
    password_reset_at = Column(DateTime(timezone=True), nullable=True)
    
    # Email verification
    email_verification_token = Column(String(255), nullable=True, index=True)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Login tracking
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    login_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"