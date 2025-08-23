"""
User Service Layer
Handles all business logic related to user operations
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user import (
    UserCreate, 
    UserUpdate, 
    AdminUserCreate,
    AdminUserUpdate,
    UserPasswordUpdate
)
from app.services.auth import AuthService, SecurityService


class UserService:
    """Service class for user-related business logic"""
    
    @staticmethod
    async def get_user_by_id(
        db: AsyncSession, 
        user_id: UUID
    ) -> Optional[User]:
        """Get user by ID"""
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_email(
        db: AsyncSession, 
        email: str
    ) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_username(
        db: AsyncSession, 
        username: str
    ) -> Optional[User]:
        """Get user by username"""
        result = await db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_users(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
        is_superuser: Optional[bool] = None
    ) -> List[User]:
        """List users with optional filters"""
        query = select(User)
        
        # Apply filters
        if search:
            query = query.where(
                or_(
                    User.email.ilike(f"%{search}%"),
                    User.username.ilike(f"%{search}%"),
                    User.full_name.ilike(f"%{search}%")
                )
            )
        
        if is_active is not None:
            query = query.where(User.is_active == is_active)
        
        if is_verified is not None:
            query = query.where(User.is_verified == is_verified)
        
        if is_superuser is not None:
            query = query.where(User.is_superuser == is_superuser)
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def create_user(
        db: AsyncSession,
        user_create: UserCreate,
        is_verified: bool = False,
        is_superuser: bool = False
    ) -> User:
        """Create a new user"""
        # Check if email already exists
        existing_user = await UserService.get_user_by_email(db, user_create.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username already exists
        if user_create.username:
            existing_user = await UserService.get_user_by_username(db, user_create.username)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # Validate password strength
        is_valid, errors = SecurityService.validate_password_strength(user_create.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Password does not meet requirements", "errors": errors}
            )
        
        # Create user
        user_data = user_create.dict(exclude={"password"})
        user_data["hashed_password"] = AuthService.get_password_hash(user_create.password)
        user_data["is_verified"] = is_verified
        user_data["is_superuser"] = is_superuser
        
        if not is_verified:
            user_data["email_verification_token"] = AuthService.create_email_verification_token()
        
        user = User(**user_data)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def update_user(
        db: AsyncSession,
        user: User,
        user_update: UserUpdate
    ) -> User:
        """Update user information"""
        # Check if email is being changed and if it's already taken
        if user_update.email and user_update.email != user.email:
            existing_user = await UserService.get_user_by_email(db, user_update.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
            # If email is changed, user needs to verify it again
            user.is_verified = False
            user.email_verification_token = AuthService.create_email_verification_token()
        
        # Check if username is being changed and if it's already taken
        if user_update.username and user_update.username != user.username:
            existing_user = await UserService.get_user_by_username(db, user_update.username)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # Update user fields
        update_data = user_update.dict(exclude_unset=True)
        
        # Handle password update separately for security
        if "password" in update_data:
            # Validate password strength
            is_valid, errors = SecurityService.validate_password_strength(update_data["password"])
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"message": "Password does not meet requirements", "errors": errors}
                )
            
            user.hashed_password = AuthService.get_password_hash(update_data["password"])
            del update_data["password"]
        
        # Update other fields
        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def update_password(
        db: AsyncSession,
        user: User,
        password_update: UserPasswordUpdate
    ) -> User:
        """Update user password"""
        # Verify current password
        if not AuthService.verify_password(password_update.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Validate new password strength
        is_valid, errors = SecurityService.validate_password_strength(password_update.new_password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Password does not meet requirements", "errors": errors}
            )
        
        # Update password
        user.hashed_password = AuthService.get_password_hash(password_update.new_password)
        user.password_changed_at = datetime.now(timezone.utc)
        
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def delete_user(
        db: AsyncSession,
        user: User,
        soft_delete: bool = True
    ) -> bool:
        """Delete or deactivate user"""
        if soft_delete:
            user.is_active = False
            user.deleted_at = datetime.now(timezone.utc)
            await db.commit()
        else:
            await db.delete(user)
            await db.commit()
        
        return True
    
    @staticmethod
    async def verify_email(
        db: AsyncSession,
        user: User
    ) -> User:
        """Mark user's email as verified"""
        user.is_verified = True
        user.email_verification_token = None
        user.email_verified_at = datetime.now(timezone.utc)
        
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def get_user_statistics(
        db: AsyncSession,
        user: User
    ) -> Dict[str, Any]:
        """Get user statistics"""
        from app.models.item import Item
        
        # Get user's items count
        items_count_result = await db.execute(
            select(func.count(Item.id)).where(Item.owner_id == user.id)
        )
        items_count = items_count_result.scalar() or 0
        
        # Get user's active items count
        active_items_result = await db.execute(
            select(func.count(Item.id)).where(
                Item.owner_id == user.id,
                Item.is_active == True
            )
        )
        active_items_count = active_items_result.scalar() or 0
        
        return {
            "total_items": items_count,
            "active_items": active_items_count,
            "account_created": user.created_at,
            "email_verified": user.is_verified,
            "last_login": user.last_login,
            "profile_completeness": UserService._calculate_profile_completeness(user)
        }
    
    @staticmethod
    def _calculate_profile_completeness(user: User) -> int:
        """Calculate user profile completeness percentage"""
        total_fields = 5
        completed_fields = 0
        
        if user.email:
            completed_fields += 1
        if user.username:
            completed_fields += 1
        if user.full_name:
            completed_fields += 1
        if user.is_verified:
            completed_fields += 1
        if user.phone_number:
            completed_fields += 1
        
        return int((completed_fields / total_fields) * 100)
    
    @staticmethod
    async def export_user_data(
        db: AsyncSession,
        user: User,
        include_items: bool = True
    ) -> Dict[str, Any]:
        """Export all user data for GDPR compliance"""
        user_data = {
            "user_info": {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "phone_number": user.phone_number,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
        }
        
        if include_items:
            from app.models.item import Item
            
            result = await db.execute(
                select(Item).where(Item.owner_id == user.id)
            )
            items = result.scalars().all()
            
            user_data["items"] = [
                {
                    "id": str(item.id),
                    "title": item.title,
                    "description": item.description,
                    "price": float(item.price) if item.price else None,
                    "is_active": item.is_active,
                    "created_at": item.created_at.isoformat() if item.created_at else None
                }
                for item in items
            ]
        
        user_data["export_date"] = datetime.now(timezone.utc).isoformat()
        user_data["total_items"] = len(user_data.get("items", []))
        
        return user_data