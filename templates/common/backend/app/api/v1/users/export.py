"""
User Data Export Endpoints
Handles user data export functionality
"""
from typing import Any
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.dependencies import (
    get_current_active_user,
    get_async_db
)
from app.models.user import User

router = APIRouter()


@router.get("/me/export")
async def export_user_data(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Export all user data as JSON
    """
    from app.models.item import Item
    
    # Get user's items
    items_result = await db.execute(
        select(Item).where(Item.owner_id == current_user.id)
    )
    items = items_result.scalars().all()
    
    export_data = {
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "username": current_user.username,
            "full_name": current_user.full_name,
            "is_active": current_user.is_active,
            "is_verified": current_user.is_verified,
            "is_superuser": current_user.is_superuser,
            "created_at": current_user.created_at.isoformat(),
            "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None,
            "login_count": current_user.login_count,
            "last_login": current_user.last_login_at.isoformat() if current_user.last_login_at else None
        },
        "items": [
            {
                "id": item.id,
                "title": item.title,
                "description": item.description,
                "created_at": item.created_at.isoformat(),
                "updated_at": item.updated_at.isoformat() if item.updated_at else None
            }
            for item in items
        ],
        "export_date": datetime.now(timezone.utc).isoformat(),
        "total_items": len(items)
    }
    
    now = datetime.now(timezone.utc)
    return JSONResponse(
        content=export_data,
        headers={
            "Content-Disposition": f"attachment; filename=user_data_{current_user.id}_{now.strftime('%Y%m%d_%H%M%S')}.json"
        }
    )