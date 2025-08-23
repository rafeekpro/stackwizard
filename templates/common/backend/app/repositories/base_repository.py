"""
Base Repository Pattern
Provides data access abstraction layer
"""
from typing import TypeVar, Generic, Type, Optional, List, Dict, Any, Union
from datetime import datetime, timezone
from uuid import UUID
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_, desc, asc
from sqlalchemy.orm import DeclarativeMeta, selectinload, joinedload
from sqlalchemy.sql import Select

from app.core.exceptions import (
    ResourceNotFoundException,
    DatabaseException,
    DatabaseTransactionException
)

# Type variables for generic model type
ModelType = TypeVar("ModelType", bound=DeclarativeMeta)

logger = logging.getLogger(__name__)


class BaseRepository(Generic[ModelType]):
    """
    Base repository class providing common database operations
    Implements Repository Pattern for data access layer
    """
    
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        """
        Initialize repository with model and database session
        
        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db
        self.model_name = model.__name__
    
    async def get(
        self,
        id: UUID,
        load_relationships: Optional[List[str]] = None
    ) -> Optional[ModelType]:
        """
        Get single entity by ID with optional relationship loading
        
        Args:
            id: Entity ID
            load_relationships: List of relationship names to eager load
            
        Returns:
            Entity or None
        """
        try:
            query = select(self.model).where(self.model.id == id)
            
            # Eager load relationships if specified
            if load_relationships:
                for relationship in load_relationships:
                    if hasattr(self.model, relationship):
                        query = query.options(selectinload(getattr(self.model, relationship)))
            
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error getting {self.model_name} by ID {id}: {str(e)}")
            raise DatabaseException(f"Failed to get {self.model_name}")
    
    async def get_by(
        self,
        load_relationships: Optional[List[str]] = None,
        **filters
    ) -> Optional[ModelType]:
        """
        Get single entity by field filters
        
        Args:
            load_relationships: List of relationship names to eager load
            **filters: Field-value pairs to filter by
            
        Returns:
            Entity or None
        """
        try:
            query = select(self.model)
            
            # Apply filters
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)
            
            # Eager load relationships
            if load_relationships:
                for relationship in load_relationships:
                    if hasattr(self.model, relationship):
                        query = query.options(selectinload(getattr(self.model, relationship)))
            
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error getting {self.model_name} by filters: {str(e)}")
            raise DatabaseException(f"Failed to get {self.model_name}")
    
    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        load_relationships: Optional[List[str]] = None,
        **filters
    ) -> List[ModelType]:
        """
        Get multiple entities with pagination and filtering
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field name to order by
            order_desc: Order descending if True
            load_relationships: List of relationship names to eager load
            **filters: Field-value pairs to filter by
            
        Returns:
            List of entities
        """
        try:
            query = select(self.model)
            
            # Apply filters
            for field, value in filters.items():
                if hasattr(self.model, field):
                    if value is not None:
                        query = query.where(getattr(self.model, field) == value)
            
            # Apply ordering
            if order_by and hasattr(self.model, order_by):
                order_field = getattr(self.model, order_by)
                query = query.order_by(desc(order_field) if order_desc else asc(order_field))
            
            # Eager load relationships
            if load_relationships:
                for relationship in load_relationships:
                    if hasattr(self.model, relationship):
                        query = query.options(selectinload(getattr(self.model, relationship)))
            
            # Apply pagination
            query = query.offset(skip).limit(limit)
            
            result = await self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting multiple {self.model_name}s: {str(e)}")
            raise DatabaseException(f"Failed to get {self.model_name}s")
    
    async def create(self, **data) -> ModelType:
        """
        Create new entity
        
        Args:
            **data: Field-value pairs for new entity
            
        Returns:
            Created entity
        """
        try:
            # Add timestamps if model has them
            if hasattr(self.model, 'created_at'):
                data['created_at'] = datetime.now(timezone.utc)
            if hasattr(self.model, 'updated_at'):
                data['updated_at'] = datetime.now(timezone.utc)
            
            entity = self.model(**data)
            self.db.add(entity)
            await self.db.commit()
            await self.db.refresh(entity)
            
            logger.info(f"Created {self.model_name} with ID: {entity.id}")
            return entity
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating {self.model_name}: {str(e)}")
            raise DatabaseTransactionException(f"create {self.model_name}")
    
    async def update(
        self,
        id: UUID,
        **data
    ) -> Optional[ModelType]:
        """
        Update entity by ID
        
        Args:
            id: Entity ID
            **data: Field-value pairs to update
            
        Returns:
            Updated entity or None if not found
        """
        try:
            entity = await self.get(id)
            if not entity:
                return None
            
            # Update fields
            for field, value in data.items():
                if hasattr(entity, field):
                    setattr(entity, field, value)
            
            # Update timestamp if model has it
            if hasattr(entity, 'updated_at'):
                entity.updated_at = datetime.now(timezone.utc)
            
            await self.db.commit()
            await self.db.refresh(entity)
            
            logger.info(f"Updated {self.model_name} with ID: {id}")
            return entity
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating {self.model_name}: {str(e)}")
            raise DatabaseTransactionException(f"update {self.model_name}")
    
    async def delete(self, id: UUID) -> bool:
        """
        Delete entity by ID (hard delete)
        
        Args:
            id: Entity ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            entity = await self.get(id)
            if not entity:
                return False
            
            await self.db.delete(entity)
            await self.db.commit()
            
            logger.info(f"Deleted {self.model_name} with ID: {id}")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting {self.model_name}: {str(e)}")
            raise DatabaseTransactionException(f"delete {self.model_name}")
    
    async def soft_delete(self, id: UUID) -> bool:
        """
        Soft delete entity by ID
        
        Args:
            id: Entity ID
            
        Returns:
            True if soft deleted, False if not found
        """
        try:
            entity = await self.get(id)
            if not entity:
                return False
            
            if hasattr(entity, 'is_active'):
                entity.is_active = False
            if hasattr(entity, 'deleted_at'):
                entity.deleted_at = datetime.now(timezone.utc)
            
            await self.db.commit()
            
            logger.info(f"Soft deleted {self.model_name} with ID: {id}")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error soft deleting {self.model_name}: {str(e)}")
            raise DatabaseTransactionException(f"soft delete {self.model_name}")
    
    async def count(self, **filters) -> int:
        """
        Count entities with optional filtering
        
        Args:
            **filters: Field-value pairs to filter by
            
        Returns:
            Count of entities
        """
        try:
            query = select(func.count(self.model.id))
            
            # Apply filters
            for field, value in filters.items():
                if hasattr(self.model, field):
                    if value is not None:
                        query = query.where(getattr(self.model, field) == value)
            
            result = await self.db.execute(query)
            return result.scalar() or 0
            
        except Exception as e:
            logger.error(f"Error counting {self.model_name}s: {str(e)}")
            raise DatabaseException(f"Failed to count {self.model_name}s")
    
    async def exists(self, **filters) -> bool:
        """
        Check if entity exists with given filters
        
        Args:
            **filters: Field-value pairs to filter by
            
        Returns:
            True if exists, False otherwise
        """
        try:
            query = select(self.model.id)
            
            # Apply filters
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)
            
            query = query.limit(1)
            result = await self.db.execute(query)
            return result.scalar() is not None
            
        except Exception as e:
            logger.error(f"Error checking {self.model_name} existence: {str(e)}")
            raise DatabaseException(f"Failed to check {self.model_name} existence")
    
    async def bulk_create(self, entities_data: List[Dict[str, Any]]) -> List[ModelType]:
        """
        Bulk create multiple entities
        
        Args:
            entities_data: List of dictionaries with entity data
            
        Returns:
            List of created entities
        """
        try:
            entities = []
            for data in entities_data:
                # Add timestamps if model has them
                if hasattr(self.model, 'created_at'):
                    data['created_at'] = datetime.now(timezone.utc)
                if hasattr(self.model, 'updated_at'):
                    data['updated_at'] = datetime.now(timezone.utc)
                
                entity = self.model(**data)
                entities.append(entity)
                self.db.add(entity)
            
            await self.db.commit()
            
            # Refresh all entities
            for entity in entities:
                await self.db.refresh(entity)
            
            logger.info(f"Bulk created {len(entities)} {self.model_name}s")
            return entities
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error bulk creating {self.model_name}s: {str(e)}")
            raise DatabaseTransactionException(f"bulk create {self.model_name}s")
    
    async def bulk_update(
        self,
        ids: List[UUID],
        **data
    ) -> int:
        """
        Bulk update multiple entities
        
        Args:
            ids: List of entity IDs to update
            **data: Field-value pairs to update
            
        Returns:
            Number of updated entities
        """
        try:
            # Add updated_at timestamp if model has it
            if hasattr(self.model, 'updated_at'):
                data['updated_at'] = datetime.now(timezone.utc)
            
            stmt = (
                update(self.model)
                .where(self.model.id.in_(ids))
                .values(**data)
            )
            
            result = await self.db.execute(stmt)
            await self.db.commit()
            
            updated_count = result.rowcount
            logger.info(f"Bulk updated {updated_count} {self.model_name}s")
            return updated_count
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error bulk updating {self.model_name}s: {str(e)}")
            raise DatabaseTransactionException(f"bulk update {self.model_name}s")
    
    async def bulk_delete(self, ids: List[UUID]) -> int:
        """
        Bulk delete multiple entities
        
        Args:
            ids: List of entity IDs to delete
            
        Returns:
            Number of deleted entities
        """
        try:
            stmt = delete(self.model).where(self.model.id.in_(ids))
            result = await self.db.execute(stmt)
            await self.db.commit()
            
            deleted_count = result.rowcount
            logger.info(f"Bulk deleted {deleted_count} {self.model_name}s")
            return deleted_count
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error bulk deleting {self.model_name}s: {str(e)}")
            raise DatabaseTransactionException(f"bulk delete {self.model_name}s")
    
    def build_search_query(
        self,
        search_term: str,
        search_fields: List[str]
    ) -> Select:
        """
        Build search query for text search across multiple fields
        
        Args:
            search_term: Search term
            search_fields: List of field names to search in
            
        Returns:
            SQLAlchemy Select query
        """
        query = select(self.model)
        
        if search_term and search_fields:
            conditions = []
            for field in search_fields:
                if hasattr(self.model, field):
                    column = getattr(self.model, field)
                    conditions.append(column.ilike(f"%{search_term}%"))
            
            if conditions:
                query = query.where(or_(*conditions))
        
        return query