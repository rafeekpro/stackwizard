"""
Refactored Items API endpoints using Service Layer
Clean separation of concerns with business logic in ItemService
"""
from typing import Any, List, Optional
from uuid import UUID
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import (
    get_current_active_user,
    get_async_db
)
from app.models.user import User
from app.models.item import Item
from app.schemas.item import (
    Item as ItemSchema,
    ItemCreate,
    ItemUpdate,
    ItemResponse,
    MessageResponse
)
from app.services.item_service import ItemService

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=List[ItemSchema])
async def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search in title or description"),
    is_active: Optional[bool] = Query(None),
    min_price: Optional[Decimal] = Query(None, ge=0),
    max_price: Optional[Decimal] = Query(None, ge=0),
    owner_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """List items with optional filters"""
    items = await ItemService.list_items(
        db,
        skip=skip,
        limit=limit,
        search=search,
        owner_id=owner_id,
        is_active=is_active,
        min_price=min_price,
        max_price=max_price
    )
    return [ItemSchema.from_orm(item) for item in items]


@router.get("/my", response_model=List[ItemSchema])
async def list_my_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """List current user's items"""
    items = await ItemService.list_items(
        db,
        skip=skip,
        limit=limit,
        owner_id=current_user.id,
        is_active=is_active
    )
    return [ItemSchema.from_orm(item) for item in items]


@router.get("/statistics", response_model=dict)
async def get_items_statistics(
    owner_id: Optional[UUID] = Query(None, description="Filter by owner ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """Get items statistics"""
    # Non-admin users can only see their own statistics
    if not current_user.is_superuser and owner_id and owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view other users' statistics"
        )
    
    stats = await ItemService.get_item_statistics(db, owner_id)
    return stats


@router.get("/{item_id}", response_model=ItemSchema)
async def get_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """Get item by ID"""
    item = await ItemService.get_item_by_id(db, item_id, include_owner=True)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    return ItemSchema.from_orm(item)


@router.post("/", response_model=ItemResponse)
async def create_item(
    item_create: ItemCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """Create a new item"""
    item = await ItemService.create_item(db, item_create, current_user)
    
    return ItemResponse(
        message="Item created successfully",
        item=ItemSchema.from_orm(item)
    )


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: UUID,
    item_update: ItemUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """Update item"""
    item = await ItemService.get_item_by_id(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    updated_item = await ItemService.update_item(db, item, item_update, current_user)
    
    return ItemResponse(
        message="Item updated successfully",
        item=ItemSchema.from_orm(updated_item)
    )


@router.delete("/{item_id}", response_model=MessageResponse)
async def delete_item(
    item_id: UUID,
    permanent: bool = Query(False, description="Permanently delete item"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """Delete item"""
    item = await ItemService.get_item_by_id(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    await ItemService.delete_item(db, item, current_user, soft_delete=not permanent)
    
    message = "Item permanently deleted" if permanent else "Item deactivated"
    return MessageResponse(message=message)


@router.post("/{item_id}/toggle-status", response_model=ItemResponse)
async def toggle_item_status(
    item_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """Toggle item active/inactive status"""
    item = await ItemService.get_item_by_id(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    toggled_item = await ItemService.toggle_item_status(db, item, current_user)
    
    status = "activated" if toggled_item.is_active else "deactivated"
    return ItemResponse(
        message=f"Item {status} successfully",
        item=ItemSchema.from_orm(toggled_item)
    )


@router.post("/{item_id}/duplicate", response_model=ItemResponse)
async def duplicate_item(
    item_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """Create a duplicate of an existing item"""
    duplicate = await ItemService.duplicate_item(db, item_id, current_user)
    
    return ItemResponse(
        message="Item duplicated successfully",
        item=ItemSchema.from_orm(duplicate)
    )


@router.post("/bulk-update", response_model=MessageResponse)
async def bulk_update_items(
    item_ids: List[UUID],
    update_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """Bulk update multiple items"""
    if not item_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No item IDs provided"
        )
    
    # Validate update data
    allowed_fields = {"is_active", "tags", "price"}
    update_fields = {k: v for k, v in update_data.items() if k in allowed_fields}
    
    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid update fields provided"
        )
    
    updated_count = await ItemService.bulk_update_items(
        db, item_ids, update_fields, current_user
    )
    
    return MessageResponse(message=f"Successfully updated {updated_count} items")


@router.post("/search", response_model=List[ItemSchema])
async def search_items(
    query: str,
    filters: Optional[dict] = None,
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """Advanced search for items"""
    items = await ItemService.search_items(db, query, filters)
    return [ItemSchema.from_orm(item) for item in items]