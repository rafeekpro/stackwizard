"""
User Repository
Data access layer for User model
"""
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from uuid import UUID

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Repository for User model with specialized queries
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address"""
        return await self.get_by(email=email)
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return await self.get_by(username=username)
    
    async def get_active_users(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Get all active users"""
        return await self.get_multi(
            skip=skip,
            limit=limit,
            is_active=True,
            order_by="created_at",
            order_desc=True
        )
    
    async def get_verified_users(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Get all verified users"""
        return await self.get_multi(
            skip=skip,
            limit=limit,
            is_verified=True,
            order_by="created_at",
            order_desc=True
        )
    
    async def get_superusers(self) -> List[User]:
        """Get all superuser accounts"""
        return await self.get_multi(is_superuser=True)
    
    async def search_users(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """
        Search users by email, username, or full name
        """
        query = self.build_search_query(
            search_term,
            ["email", "username", "full_name"]
        )
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_recent_users(
        self,
        days: int = 7,
        limit: int = 50
    ) -> List[User]:
        """Get recently registered users"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        query = select(User).where(
            User.created_at >= cutoff_date
        ).order_by(User.created_at.desc()).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_inactive_users(
        self,
        days_inactive: int = 30
    ) -> List[User]:
        """Get users who haven't logged in for specified days"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_inactive)
        
        query = select(User).where(
            or_(
                User.last_login < cutoff_date,
                User.last_login.is_(None)
            )
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def count_by_status(self) -> dict:
        """Get user counts grouped by status"""
        # Total users
        total = await self.count()
        
        # Active users
        active = await self.count(is_active=True)
        
        # Verified users
        verified = await self.count(is_verified=True)
        
        # Superusers
        superusers = await self.count(is_superuser=True)
        
        return {
            "total": total,
            "active": active,
            "inactive": total - active,
            "verified": verified,
            "unverified": total - verified,
            "superusers": superusers
        }
    
    async def update_last_login(self, user_id: UUID) -> bool:
        """Update user's last login timestamp"""
        return await self.update(
            user_id,
            last_login=datetime.now(timezone.utc)
        ) is not None
    
    async def verify_user(self, user_id: UUID) -> bool:
        """Mark user as verified"""
        return await self.update(
            user_id,
            is_verified=True,
            email_verified_at=datetime.now(timezone.utc),
            email_verification_token=None
        ) is not None
    
    async def activate_user(self, user_id: UUID) -> bool:
        """Activate user account"""
        return await self.update(
            user_id,
            is_active=True,
            deleted_at=None
        ) is not None
    
    async def deactivate_user(self, user_id: UUID) -> bool:
        """Deactivate user account"""
        return await self.update(
            user_id,
            is_active=False,
            deleted_at=datetime.now(timezone.utc)
        ) is not None
    
    async def update_password(
        self,
        user_id: UUID,
        hashed_password: str
    ) -> bool:
        """Update user's password"""
        return await self.update(
            user_id,
            hashed_password=hashed_password,
            password_changed_at=datetime.now(timezone.utc)
        ) is not None
    
    async def get_user_statistics(self, user_id: UUID) -> dict:
        """Get detailed statistics for a user"""
        from app.models.item import Item
        
        # Get user
        user = await self.get(user_id)
        if not user:
            return {}
        
        # Count user's items
        items_query = select(func.count(Item.id)).where(Item.owner_id == user_id)
        items_result = await self.db.execute(items_query)
        total_items = items_result.scalar() or 0
        
        # Count active items
        active_items_query = select(func.count(Item.id)).where(
            and_(Item.owner_id == user_id, Item.is_active == True)
        )
        active_items_result = await self.db.execute(active_items_query)
        active_items = active_items_result.scalar() or 0
        
        return {
            "user_id": str(user_id),
            "account_age_days": (datetime.now(timezone.utc) - user.created_at).days if user.created_at else 0,
            "total_items": total_items,
            "active_items": active_items,
            "inactive_items": total_items - active_items,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }