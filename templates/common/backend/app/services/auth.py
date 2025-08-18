from datetime import datetime, timedelta
from typing import Optional, Union
from uuid import UUID
import secrets

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from email_validator import validate_email

from app.core.config import settings
from app.models.user import User
from app.schemas.user import TokenData

# Password hashing context
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__rounds=settings.BCRYPT_ROUNDS
)

class AuthService:
    """Authentication service for handling JWT tokens and password operations"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate password hash"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(
        data: dict, 
        expires_delta: Optional[timedelta] = None,
        scopes: list[str] = None
    ) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({
            "exp": expire,
            "scopes": scopes or [],
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({
            "exp": expire,
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[TokenData]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            user_id: str = payload.get("sub")
            token_type: str = payload.get("type")
            scopes: list = payload.get("scopes", [])
            
            if user_id is None:
                return None
                
            token_data = TokenData(
                user_id=UUID(user_id), 
                scopes=scopes
            )
            return token_data
            
        except (JWTError, ValueError):
            return None
    
    @staticmethod
    def create_password_reset_token() -> str:
        """Generate a secure password reset token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def create_email_verification_token() -> str:
        """Generate a secure email verification token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def validate_email_format(email: str) -> bool:
        """Validate email format"""
        try:
            validate_email(email)
            return True
        except Exception:
            return False
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email from database"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
        """Get user by ID from database"""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_reset_token(db: AsyncSession, token: str) -> Optional[User]:
        """Get user by password reset token"""
        result = await db.execute(
            select(User).where(
                User.password_reset_token == token,
                User.password_reset_at > datetime.utcnow() - timedelta(
                    hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS
                )
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_verification_token(db: AsyncSession, token: str) -> Optional[User]:
        """Get user by email verification token"""
        result = await db.execute(
            select(User).where(User.email_verification_token == token)
        )
        return result.scalar_one_or_none()
    
    @classmethod
    async def authenticate_user(
        cls, 
        db: AsyncSession, 
        email: str, 
        password: str
    ) -> Optional[User]:
        """Authenticate user with email and password"""
        user = await cls.get_user_by_email(db, email)
        if not user:
            return None
        if not cls.verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user
    
    @staticmethod
    async def update_last_login(db: AsyncSession, user: User) -> None:
        """Update user's last login timestamp and count"""
        user.last_login_at = datetime.utcnow()
        user.login_count += 1
        await db.commit()
        await db.refresh(user)

class SecurityService:
    """Security utilities and validation"""
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, list[str]]:
        """Validate password strength and return errors if any"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if len(password) > 128:
            errors.append("Password must be no more than 128 characters long")
        
        if not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one digit")
        
        # Optional: Special characters
        # if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        #     errors.append("Password must contain at least one special character")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def generate_secure_password(length: int = 12) -> str:
        """Generate a secure random password"""
        import string
        import random
        
        # Ensure we have at least one character from each required category
        password = [
            random.choice(string.ascii_lowercase),
            random.choice(string.ascii_uppercase),
            random.choice(string.digits),
            random.choice("!@#$%^&*")
        ]
        
        # Fill the rest randomly
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        for _ in range(length - 4):
            password.append(random.choice(chars))
        
        # Shuffle the password list
        random.shuffle(password)
        return ''.join(password)