"""
Base Service Class
Provides common functionality for all service classes
"""
from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from datetime import datetime, timezone
from uuid import UUID
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import DeclarativeMeta
from fastapi import HTTPException, status

# Type variables for generic model and schema types
ModelType = TypeVar("ModelType", bound=DeclarativeMeta)
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")

logger = logging.getLogger(__name__)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base service class with common CRUD operations
    Provides reusable methods for all service classes
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        Initialize base service with model class
        
        Args:
            model: SQLAlchemy model class
        """
        self.model = model
        self.model_name = model.__name__
    
    async def get_by_id(
        self,
        db: AsyncSession,
        id: UUID,
        raise_not_found: bool = False
    ) -> Optional[ModelType]:
        """
        Get entity by ID
        
        Args:
            db: Database session
            id: Entity ID
            raise_not_found: Raise exception if not found
            
        Returns:
            Entity or None
            
        Raises:
            HTTPException: If entity not found and raise_not_found is True
        """
        try:
            result = await db.execute(
                select(self.model).where(self.model.id == id)
            )
            entity = result.scalar_one_or_none()
            
            if not entity and raise_not_found:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{self.model_name} not found"
                )
            
            return entity
            
        except Exception as e:
            logger.error(f"Error getting {self.model_name} by ID: {str(e)}")
            if raise_not_found:
                raise
            return None
    
    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        Get all entities with optional filtering
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Optional filters to apply
            
        Returns:
            List of entities
        """
        try:
            query = select(self.model)
            
            # Apply filters if provided
            if filters:
                conditions = []
                for field, value in filters.items():
                    if hasattr(self.model, field):
                        conditions.append(getattr(self.model, field) == value)
                
                if conditions:
                    query = query.where(and_(*conditions))
            
            # Apply pagination
            query = query.offset(skip).limit(limit)
            
            result = await db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting all {self.model_name}s: {str(e)}")
            return []
    
    async def create(
        self,
        db: AsyncSession,
        obj_in: CreateSchemaType,
        **extra_fields
    ) -> ModelType:
        """
        Create new entity
        
        Args:
            db: Database session
            obj_in: Creation schema
            **extra_fields: Additional fields to set
            
        Returns:
            Created entity
        """
        try:
            # Convert schema to dict
            if hasattr(obj_in, 'dict'):
                data = obj_in.dict(exclude_unset=True)
            else:
                data = dict(obj_in)
            
            # Add extra fields
            data.update(extra_fields)
            
            # Create entity
            entity = self.model(**data)
            db.add(entity)
            await db.commit()
            await db.refresh(entity)
            
            logger.info(f"Created {self.model_name} with ID: {entity.id}")
            return entity
            
        except Exception as e:
            logger.error(f"Error creating {self.model_name}: {str(e)}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error creating {self.model_name}: {str(e)}"
            )
    
    async def update(
        self,
        db: AsyncSession,
        entity: ModelType,
        obj_in: UpdateSchemaType
    ) -> ModelType:
        """
        Update existing entity
        
        Args:
            db: Database session
            entity: Entity to update
            obj_in: Update schema
            
        Returns:
            Updated entity
        """
        try:
            # Convert schema to dict
            if hasattr(obj_in, 'dict'):
                update_data = obj_in.dict(exclude_unset=True)
            else:
                update_data = dict(obj_in)
            
            # Update fields
            for field, value in update_data.items():
                if hasattr(entity, field):
                    setattr(entity, field, value)
            
            # Update timestamp if available
            if hasattr(entity, 'updated_at'):
                entity.updated_at = datetime.now(timezone.utc)
            
            await db.commit()
            await db.refresh(entity)
            
            logger.info(f"Updated {self.model_name} with ID: {entity.id}")
            return entity
            
        except Exception as e:
            logger.error(f"Error updating {self.model_name}: {str(e)}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error updating {self.model_name}: {str(e)}"
            )
    
    async def delete(
        self,
        db: AsyncSession,
        entity: ModelType,
        soft_delete: bool = True
    ) -> bool:
        """
        Delete entity (soft or hard delete)
        
        Args:
            db: Database session
            entity: Entity to delete
            soft_delete: If True, soft delete; otherwise hard delete
            
        Returns:
            True if successful
        """
        try:
            if soft_delete and hasattr(entity, 'is_active'):
                # Soft delete
                entity.is_active = False
                if hasattr(entity, 'deleted_at'):
                    entity.deleted_at = datetime.now(timezone.utc)
                await db.commit()
                logger.info(f"Soft deleted {self.model_name} with ID: {entity.id}")
            else:
                # Hard delete
                await db.delete(entity)
                await db.commit()
                logger.info(f"Hard deleted {self.model_name} with ID: {entity.id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting {self.model_name}: {str(e)}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error deleting {self.model_name}: {str(e)}"
            )
    
    async def count(
        self,
        db: AsyncSession,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Count entities with optional filtering
        
        Args:
            db: Database session
            filters: Optional filters to apply
            
        Returns:
            Count of entities
        """
        try:
            query = select(func.count(self.model.id))
            
            # Apply filters if provided
            if filters:
                conditions = []
                for field, value in filters.items():
                    if hasattr(self.model, field):
                        conditions.append(getattr(self.model, field) == value)
                
                if conditions:
                    query = query.where(and_(*conditions))
            
            result = await db.execute(query)
            return result.scalar() or 0
            
        except Exception as e:
            logger.error(f"Error counting {self.model_name}s: {str(e)}")
            return 0
    
    async def exists(
        self,
        db: AsyncSession,
        **filters
    ) -> bool:
        """
        Check if entity exists with given filters
        
        Args:
            db: Database session
            **filters: Field filters
            
        Returns:
            True if exists, False otherwise
        """
        try:
            query = select(self.model.id)
            
            conditions = []
            for field, value in filters.items():
                if hasattr(self.model, field):
                    conditions.append(getattr(self.model, field) == value)
            
            if conditions:
                query = query.where(and_(*conditions))
                result = await db.execute(query.limit(1))
                return result.scalar() is not None
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking {self.model_name} existence: {str(e)}")
            return False
    
    async def bulk_create(
        self,
        db: AsyncSession,
        objects_in: List[CreateSchemaType]
    ) -> List[ModelType]:
        """
        Bulk create multiple entities
        
        Args:
            db: Database session
            objects_in: List of creation schemas
            
        Returns:
            List of created entities
        """
        try:
            entities = []
            for obj_in in objects_in:
                if hasattr(obj_in, 'dict'):
                    data = obj_in.dict(exclude_unset=True)
                else:
                    data = dict(obj_in)
                
                entity = self.model(**data)
                entities.append(entity)
                db.add(entity)
            
            await db.commit()
            
            # Refresh all entities
            for entity in entities:
                await db.refresh(entity)
            
            logger.info(f"Bulk created {len(entities)} {self.model_name}s")
            return entities
            
        except Exception as e:
            logger.error(f"Error bulk creating {self.model_name}s: {str(e)}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error bulk creating {self.model_name}s: {str(e)}"
            )
    
    async def bulk_update(
        self,
        db: AsyncSession,
        entities: List[ModelType],
        update_data: Dict[str, Any]
    ) -> int:
        """
        Bulk update multiple entities
        
        Args:
            db: Database session
            entities: List of entities to update
            update_data: Data to update
            
        Returns:
            Number of updated entities
        """
        try:
            updated_count = 0
            
            for entity in entities:
                for field, value in update_data.items():
                    if hasattr(entity, field):
                        setattr(entity, field, value)
                
                if hasattr(entity, 'updated_at'):
                    entity.updated_at = datetime.now(timezone.utc)
                
                updated_count += 1
            
            await db.commit()
            
            logger.info(f"Bulk updated {updated_count} {self.model_name}s")
            return updated_count
            
        except Exception as e:
            logger.error(f"Error bulk updating {self.model_name}s: {str(e)}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error bulk updating {self.model_name}s: {str(e)}"
            )
    
    async def search(
        self,
        db: AsyncSession,
        search_term: str,
        search_fields: List[str],
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        Search entities by term in specified fields
        
        Args:
            db: Database session
            search_term: Search term
            search_fields: Fields to search in
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching entities
        """
        try:
            query = select(self.model)
            
            # Build search conditions
            conditions = []
            for field in search_fields:
                if hasattr(self.model, field):
                    column = getattr(self.model, field)
                    conditions.append(column.ilike(f"%{search_term}%"))
            
            if conditions:
                query = query.where(or_(*conditions))
            
            # Apply pagination
            query = query.offset(skip).limit(limit)
            
            result = await db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error searching {self.model_name}s: {str(e)}")
            return []