"""
Item Service Layer
Handles all business logic related to item operations
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from uuid import UUID
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.item import Item
from app.models.user import User
from app.schemas.item import ItemCreate, ItemUpdate


class ItemService:
    """Service class for item-related business logic"""
    
    @staticmethod
    async def get_item_by_id(
        db: AsyncSession,
        item_id: UUID,
        include_owner: bool = False
    ) -> Optional[Item]:
        """Get item by ID with optional owner data"""
        query = select(Item).where(Item.id == item_id)
        
        if include_owner:
            query = query.options(selectinload(Item.owner))
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_items(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        owner_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        tags: Optional[List[str]] = None
    ) -> List[Item]:
        """List items with optional filters"""
        query = select(Item)
        
        # Apply filters
        conditions = []
        
        if search:
            conditions.append(
                or_(
                    Item.title.ilike(f"%{search}%"),
                    Item.description.ilike(f"%{search}%")
                )
            )
        
        if owner_id:
            conditions.append(Item.owner_id == owner_id)
        
        if is_active is not None:
            conditions.append(Item.is_active == is_active)
        
        if min_price is not None:
            conditions.append(Item.price >= min_price)
        
        if max_price is not None:
            conditions.append(Item.price <= max_price)
        
        if tags:
            # Assuming tags are stored as JSON array
            for tag in tags:
                conditions.append(Item.tags.contains([tag]))
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Include owner data
        query = query.options(selectinload(Item.owner))
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def create_item(
        db: AsyncSession,
        item_create: ItemCreate,
        owner: User
    ) -> Item:
        """Create a new item"""
        # Validate price if provided
        if item_create.price and item_create.price < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Price cannot be negative"
            )
        
        # Create item
        item_data = item_create.dict()
        item_data["owner_id"] = owner.id
        
        item = Item(**item_data)
        db.add(item)
        await db.commit()
        await db.refresh(item)
        
        # Load owner relationship
        await db.refresh(item, ["owner"])
        
        return item
    
    @staticmethod
    async def update_item(
        db: AsyncSession,
        item: Item,
        item_update: ItemUpdate,
        current_user: User
    ) -> Item:
        """Update item information"""
        # Check ownership
        if item.owner_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to update this item"
            )
        
        # Validate price if being updated
        if item_update.price is not None and item_update.price < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Price cannot be negative"
            )
        
        # Update item fields
        update_data = item_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(item, field):
                setattr(item, field, value)
        
        item.updated_at = datetime.now(timezone.utc)
        
        await db.commit()
        await db.refresh(item)
        
        return item
    
    @staticmethod
    async def delete_item(
        db: AsyncSession,
        item: Item,
        current_user: User,
        soft_delete: bool = True
    ) -> bool:
        """Delete or deactivate item"""
        # Check ownership
        if item.owner_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to delete this item"
            )
        
        if soft_delete:
            item.is_active = False
            item.deleted_at = datetime.now(timezone.utc)
            await db.commit()
        else:
            await db.delete(item)
            await db.commit()
        
        return True
    
    @staticmethod
    async def toggle_item_status(
        db: AsyncSession,
        item: Item,
        current_user: User
    ) -> Item:
        """Toggle item active status"""
        # Check ownership
        if item.owner_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to modify this item"
            )
        
        item.is_active = not item.is_active
        item.updated_at = datetime.now(timezone.utc)
        
        await db.commit()
        await db.refresh(item)
        
        return item
    
    @staticmethod
    async def get_item_statistics(
        db: AsyncSession,
        owner_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Get item statistics"""
        base_query = select(Item)
        
        if owner_id:
            base_query = base_query.where(Item.owner_id == owner_id)
        
        # Total items count
        total_result = await db.execute(
            select(func.count(Item.id)).select_from(base_query.subquery())
        )
        total_items = total_result.scalar() or 0
        
        # Active items count
        active_query = base_query.where(Item.is_active == True)
        active_result = await db.execute(
            select(func.count(Item.id)).select_from(active_query.subquery())
        )
        active_items = active_result.scalar() or 0
        
        # Average price
        price_result = await db.execute(
            select(func.avg(Item.price)).select_from(base_query.subquery())
        )
        avg_price = price_result.scalar()
        
        # Price range
        min_price_result = await db.execute(
            select(func.min(Item.price)).select_from(base_query.subquery())
        )
        min_price = min_price_result.scalar()
        
        max_price_result = await db.execute(
            select(func.max(Item.price)).select_from(base_query.subquery())
        )
        max_price = max_price_result.scalar()
        
        return {
            "total_items": total_items,
            "active_items": active_items,
            "inactive_items": total_items - active_items,
            "average_price": float(avg_price) if avg_price else 0,
            "min_price": float(min_price) if min_price else 0,
            "max_price": float(max_price) if max_price else 0,
            "activity_rate": (active_items / total_items * 100) if total_items > 0 else 0
        }
    
    @staticmethod
    async def bulk_update_items(
        db: AsyncSession,
        item_ids: List[UUID],
        update_data: Dict[str, Any],
        current_user: User
    ) -> int:
        """Bulk update multiple items"""
        # Get items and verify ownership
        result = await db.execute(
            select(Item).where(Item.id.in_(item_ids))
        )
        items = result.scalars().all()
        
        # Check permissions for all items
        for item in items:
            if item.owner_id != current_user.id and not current_user.is_superuser:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Not enough permissions to update item {item.id}"
                )
        
        # Update items
        updated_count = 0
        for item in items:
            for field, value in update_data.items():
                if hasattr(item, field) and field not in ["id", "owner_id", "created_at"]:
                    setattr(item, field, value)
            item.updated_at = datetime.now(timezone.utc)
            updated_count += 1
        
        await db.commit()
        
        return updated_count
    
    @staticmethod
    async def duplicate_item(
        db: AsyncSession,
        item_id: UUID,
        current_user: User
    ) -> Item:
        """Create a duplicate of an existing item"""
        # Get original item
        original = await ItemService.get_item_by_id(db, item_id)
        
        if not original:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        
        # Check ownership
        if original.owner_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to duplicate this item"
            )
        
        # Create duplicate
        duplicate_data = {
            "title": f"{original.title} (Copy)",
            "description": original.description,
            "price": original.price,
            "tags": original.tags,
            "is_active": False,  # Start as inactive
            "owner_id": current_user.id
        }
        
        duplicate = Item(**duplicate_data)
        db.add(duplicate)
        await db.commit()
        await db.refresh(duplicate)
        
        return duplicate
    
    @staticmethod
    async def search_items(
        db: AsyncSession,
        query: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Item]:
        """Advanced search for items"""
        # Build search query
        search_conditions = []
        
        # Text search
        if query:
            search_conditions.append(
                or_(
                    Item.title.ilike(f"%{query}%"),
                    Item.description.ilike(f"%{query}%"),
                    Item.tags.contains([query])
                )
            )
        
        # Apply additional filters
        if filters:
            if "is_active" in filters:
                search_conditions.append(Item.is_active == filters["is_active"])
            
            if "owner_id" in filters:
                search_conditions.append(Item.owner_id == filters["owner_id"])
            
            if "price_range" in filters:
                min_price, max_price = filters["price_range"]
                if min_price is not None:
                    search_conditions.append(Item.price >= min_price)
                if max_price is not None:
                    search_conditions.append(Item.price <= max_price)
            
            if "created_after" in filters:
                search_conditions.append(Item.created_at >= filters["created_after"])
            
            if "created_before" in filters:
                search_conditions.append(Item.created_at <= filters["created_before"])
        
        # Execute search
        search_query = select(Item).options(selectinload(Item.owner))
        
        if search_conditions:
            search_query = search_query.where(and_(*search_conditions))
        
        # Order by relevance (simple implementation)
        search_query = search_query.order_by(Item.updated_at.desc())
        
        result = await db.execute(search_query)
        return result.scalars().all()