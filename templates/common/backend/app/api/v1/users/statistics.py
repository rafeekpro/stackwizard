"""
User Statistics Endpoints
Provides user statistics and metrics
"""
from typing import Any, Dict
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.dependencies import (
    get_current_active_user,
    get_async_db
)
from app.models.user import User

router = APIRouter()


@router.get("/me/statistics", response_model=Dict[str, Any])
async def get_user_statistics(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Get current user statistics
    """
    from app.models.item import Item
    
    # Get items count
    items_result = await db.execute(
        select(func.count(Item.id)).where(Item.owner_id == current_user.id)
    )
    items_count = items_result.scalar() or 0
    
    # Calculate account age
    account_age = datetime.now(timezone.utc) - current_user.created_at
    
    return {
        "user_id": str(current_user.id),
        "email": current_user.email,
        "total_items": items_count,
        "login_count": current_user.login_count or 0,
        "last_login": current_user.last_login_at.isoformat() if current_user.last_login_at else None,
        "account_age_days": account_age.days,
        "email_verified": current_user.is_verified,
        "account_created": current_user.created_at.isoformat(),
        "last_updated": current_user.updated_at.isoformat() if current_user.updated_at else None,
        "is_active": current_user.is_active,
        "is_superuser": current_user.is_superuser
    }