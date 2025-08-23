"""
Admin Service Layer
Handles all business logic related to admin operations
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from uuid import UUID
import csv
import io
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from fastapi import HTTPException, status

from app.models.user import User
from app.models.item import Item


class AdminService:
    """Service class for admin-related business logic"""
    
    @staticmethod
    async def get_system_statistics(db: AsyncSession) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        # User statistics
        total_users_result = await db.execute(select(func.count(User.id)))
        total_users = total_users_result.scalar() or 0
        
        active_users_result = await db.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )
        active_users = active_users_result.scalar() or 0
        
        verified_users_result = await db.execute(
            select(func.count(User.id)).where(User.is_verified == True)
        )
        verified_users = verified_users_result.scalar() or 0
        
        admin_users_result = await db.execute(
            select(func.count(User.id)).where(User.is_superuser == True)
        )
        admin_users = admin_users_result.scalar() or 0
        
        # Item statistics
        total_items_result = await db.execute(select(func.count(Item.id)))
        total_items = total_items_result.scalar() or 0
        
        active_items_result = await db.execute(
            select(func.count(Item.id)).where(Item.is_active == True)
        )
        active_items = active_items_result.scalar() or 0
        
        # Recent activity (last 30 days)
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        
        new_users_result = await db.execute(
            select(func.count(User.id)).where(User.created_at >= thirty_days_ago)
        )
        new_users_30d = new_users_result.scalar() or 0
        
        new_items_result = await db.execute(
            select(func.count(Item.id)).where(Item.created_at >= thirty_days_ago)
        )
        new_items_30d = new_items_result.scalar() or 0
        
        # Average statistics
        avg_items_per_user_result = await db.execute(
            select(func.avg(func.count(Item.id))).select_from(
                select(User.id, func.count(Item.id))
                .select_from(User)
                .outerjoin(Item, User.id == Item.owner_id)
                .group_by(User.id)
                .subquery()
            )
        )
        avg_items_per_user = avg_items_per_user_result.scalar() or 0
        
        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "inactive": total_users - active_users,
                "verified": verified_users,
                "unverified": total_users - verified_users,
                "admins": admin_users,
                "new_last_30_days": new_users_30d
            },
            "items": {
                "total": total_items,
                "active": active_items,
                "inactive": total_items - active_items,
                "new_last_30_days": new_items_30d,
                "average_per_user": float(avg_items_per_user)
            },
            "activity_rates": {
                "user_activation_rate": (active_users / total_users * 100) if total_users > 0 else 0,
                "user_verification_rate": (verified_users / total_users * 100) if total_users > 0 else 0,
                "item_activation_rate": (active_items / total_items * 100) if total_items > 0 else 0
            },
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    @staticmethod
    async def get_recent_registrations(
        db: AsyncSession,
        days: int = 7,
        limit: int = 50
    ) -> List[User]:
        """Get recently registered users"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        result = await db.execute(
            select(User)
            .where(User.created_at >= cutoff_date)
            .order_by(desc(User.created_at))
            .limit(limit)
        )
        
        return result.scalars().all()
    
    @staticmethod
    async def get_audit_log(
        db: AsyncSession,
        user_id: Optional[UUID] = None,
        action_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get audit log entries (placeholder - implement with actual audit table)"""
        # This is a placeholder implementation
        # In production, you would query an actual audit log table
        audit_entries = []
        
        # Example audit log structure
        audit_entries.append({
            "id": "audit_001",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": str(user_id) if user_id else None,
            "action": action_type or "VIEW",
            "resource": "users",
            "details": "Viewed user list",
            "ip_address": "127.0.0.1"
        })
        
        return audit_entries
    
    @staticmethod
    async def bulk_activate_users(
        db: AsyncSession,
        user_ids: List[UUID]
    ) -> int:
        """Bulk activate multiple users"""
        result = await db.execute(
            select(User).where(User.id.in_(user_ids))
        )
        users = result.scalars().all()
        
        activated_count = 0
        for user in users:
            if not user.is_active:
                user.is_active = True
                user.updated_at = datetime.now(timezone.utc)
                activated_count += 1
        
        await db.commit()
        return activated_count
    
    @staticmethod
    async def bulk_deactivate_users(
        db: AsyncSession,
        user_ids: List[UUID],
        exclude_admins: bool = True
    ) -> int:
        """Bulk deactivate multiple users"""
        query = select(User).where(User.id.in_(user_ids))
        
        if exclude_admins:
            query = query.where(User.is_superuser == False)
        
        result = await db.execute(query)
        users = result.scalars().all()
        
        deactivated_count = 0
        for user in users:
            if user.is_active:
                user.is_active = False
                user.updated_at = datetime.now(timezone.utc)
                deactivated_count += 1
        
        await db.commit()
        return deactivated_count
    
    @staticmethod
    async def export_users_csv(
        db: AsyncSession,
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Export users to CSV format"""
        query = select(User)
        
        # Apply filters
        if filters:
            conditions = []
            if "is_active" in filters:
                conditions.append(User.is_active == filters["is_active"])
            if "is_verified" in filters:
                conditions.append(User.is_verified == filters["is_verified"])
            if "is_superuser" in filters:
                conditions.append(User.is_superuser == filters["is_superuser"])
            
            if conditions:
                query = query.where(and_(*conditions))
        
        result = await db.execute(query)
        users = result.scalars().all()
        
        # Create CSV
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "id", "email", "username", "full_name",
                "is_active", "is_verified", "is_superuser",
                "created_at", "last_login"
            ]
        )
        
        writer.writeheader()
        for user in users:
            writer.writerow({
                "id": str(user.id),
                "email": user.email,
                "username": user.username or "",
                "full_name": user.full_name or "",
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "is_superuser": user.is_superuser,
                "created_at": user.created_at.isoformat() if user.created_at else "",
                "last_login": user.last_login.isoformat() if user.last_login else ""
            })
        
        return output.getvalue()
    
    @staticmethod
    async def export_users_json(
        db: AsyncSession,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Export users to JSON format"""
        query = select(User)
        
        # Apply filters
        if filters:
            conditions = []
            if "is_active" in filters:
                conditions.append(User.is_active == filters["is_active"])
            if "is_verified" in filters:
                conditions.append(User.is_verified == filters["is_verified"])
            if "is_superuser" in filters:
                conditions.append(User.is_superuser == filters["is_superuser"])
            
            if conditions:
                query = query.where(and_(*conditions))
        
        result = await db.execute(query)
        users = result.scalars().all()
        
        return {
            "users": [
                {
                    "id": str(user.id),
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.full_name,
                    "is_active": user.is_active,
                    "is_verified": user.is_verified,
                    "is_superuser": user.is_superuser,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "last_login": user.last_login.isoformat() if user.last_login else None
                }
                for user in users
            ],
            "total": len(users),
            "export_date": datetime.now(timezone.utc).isoformat()
        }
    
    @staticmethod
    async def import_users(
        db: AsyncSession,
        users_data: List[Dict[str, Any]],
        skip_existing: bool = True
    ) -> Dict[str, Any]:
        """Import users from data"""
        from app.services.auth import AuthService
        
        imported = 0
        skipped = 0
        errors = []
        
        for user_data in users_data:
            try:
                # Check if user exists
                existing_user = await db.execute(
                    select(User).where(User.email == user_data["email"])
                )
                if existing_user.scalar_one_or_none():
                    if skip_existing:
                        skipped += 1
                        continue
                    else:
                        errors.append(f"User with email {user_data['email']} already exists")
                        continue
                
                # Create new user
                user = User(
                    email=user_data["email"],
                    username=user_data.get("username"),
                    full_name=user_data.get("full_name"),
                    hashed_password=AuthService.get_password_hash(
                        user_data.get("password", "TempPassword123!")
                    ),
                    is_active=user_data.get("is_active", True),
                    is_verified=user_data.get("is_verified", False),
                    is_superuser=user_data.get("is_superuser", False)
                )
                
                db.add(user)
                imported += 1
                
            except Exception as e:
                errors.append(f"Error importing user {user_data.get('email', 'unknown')}: {str(e)}")
        
        await db.commit()
        
        return {
            "imported": imported,
            "skipped": skipped,
            "errors": errors,
            "total_processed": len(users_data)
        }
    
    @staticmethod
    async def get_user_sessions(
        db: AsyncSession,
        user_id: UUID
    ) -> List[Dict[str, Any]]:
        """Get active sessions for a user (placeholder)"""
        # This is a placeholder implementation
        # In production, you would query actual session storage
        return [
            {
                "session_id": "session_001",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_activity": datetime.now(timezone.utc).isoformat(),
                "ip_address": "127.0.0.1",
                "user_agent": "Mozilla/5.0..."
            }
        ]
    
    @staticmethod
    async def invalidate_user_sessions(
        db: AsyncSession,
        user_id: UUID
    ) -> bool:
        """Invalidate all sessions for a user"""
        # This is a placeholder implementation
        # In production, you would invalidate actual sessions
        user_result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if user:
            # Update user to force re-authentication
            user.updated_at = datetime.now(timezone.utc)
            await db.commit()
            return True
        
        return False
    
    @staticmethod
    async def cleanup_inactive_users(
        db: AsyncSession,
        days_inactive: int = 365
    ) -> int:
        """Clean up users who haven't logged in for specified days"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_inactive)
        
        result = await db.execute(
            select(User).where(
                and_(
                    or_(
                        User.last_login < cutoff_date,
                        User.last_login.is_(None)
                    ),
                    User.is_superuser == False,
                    User.is_active == True
                )
            )
        )
        
        users = result.scalars().all()
        
        deactivated_count = 0
        for user in users:
            user.is_active = False
            user.updated_at = datetime.now(timezone.utc)
            deactivated_count += 1
        
        await db.commit()
        return deactivated_count
    
    @staticmethod
    async def get_growth_metrics(
        db: AsyncSession,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Get growth metrics for specified period"""
        now = datetime.now(timezone.utc)
        period_start = now - timedelta(days=period_days)
        previous_period_start = period_start - timedelta(days=period_days)
        
        # Current period users
        current_users_result = await db.execute(
            select(func.count(User.id)).where(
                User.created_at.between(period_start, now)
            )
        )
        current_users = current_users_result.scalar() or 0
        
        # Previous period users
        previous_users_result = await db.execute(
            select(func.count(User.id)).where(
                User.created_at.between(previous_period_start, period_start)
            )
        )
        previous_users = previous_users_result.scalar() or 0
        
        # Calculate growth rate
        growth_rate = 0
        if previous_users > 0:
            growth_rate = ((current_users - previous_users) / previous_users) * 100
        
        # Daily average
        daily_average = current_users / period_days if period_days > 0 else 0
        
        return {
            "period_days": period_days,
            "new_users_current_period": current_users,
            "new_users_previous_period": previous_users,
            "growth_rate_percentage": round(growth_rate, 2),
            "daily_average": round(daily_average, 2),
            "period_start": period_start.isoformat(),
            "period_end": now.isoformat()
        }