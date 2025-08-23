@router.get("/me/export")
async def export_user_data(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """Export all user data"""
    from fastapi.responses import JSONResponse
    from app.models.item import Item
    from datetime import datetime
    import json
    
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
            "created_at": current_user.created_at.isoformat(),
            "login_count": current_user.login_count
        },
        "items": [
            {
                "id": item.id,
                "title": item.title,
                "description": item.description,
                "created_at": item.created_at.isoformat()
            }
            for item in items
        ],
        "export_date": datetime.utcnow().isoformat()
    }
    
    return JSONResponse(
        content=export_data,
        headers={
            "Content-Disposition": f"attachment; filename=user_data_{current_user.id}.json"
        }
    )