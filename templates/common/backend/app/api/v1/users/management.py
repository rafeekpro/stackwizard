"""
User Management Endpoints
Admin operations for user management
"""
from typing import Any, List, Optional, Dict
from uuid import UUID
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func

from app.core.dependencies import (
    get_current_superuser,
    get_async_db
)
from app.models.user import User
from app.schemas.user import (
    User as UserSchema,
    AdminUserCreate,
    AdminUserUpdate,
    UserResponse,
    MessageResponse
)
from app.services.auth import AuthService, SecurityService

router = APIRouter()


@router.get("/", response_model=List[UserSchema])
async def get_all_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
    search: Optional[str] = Query(None, description="Search in email, username, or full_name"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Get all users (admin only)
    """
    # Build query with filters
    query = select(User)
    
    # Search filter
    if search:
        search_filter = or_(
            User.email.ilike(f"%{search}%"),
            User.username.ilike(f"%{search}%"),
            User.full_name.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
    
    # Status filter
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    
    # Apply pagination
    query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    return [UserSchema.from_orm(user) for user in users]


@router.get("/{user_id}", response_model=UserSchema)
async def get_user_by_id(
    user_id: UUID,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Get user by ID (admin only)
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserSchema.from_orm(user)


@router.post("/", response_model=UserResponse)
async def create_user_by_admin(
    user_data: AdminUserCreate,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Create new user (admin only)
    """
    # Check if user already exists
    existing_user = await AuthService.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Check if username is taken (if provided)
    if user_data.username:
        result = await db.execute(
            select(User).where(User.username == user_data.username)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Validate password strength
    is_valid, errors = SecurityService.validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Password does not meet requirements", "errors": errors}
        )
    
    # Create new user
    hashed_password = AuthService.get_password_hash(user_data.password)
    
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        username=user_data.username,
        full_name=user_data.full_name,
        is_active=user_data.is_active,
        is_verified=user_data.is_verified,
        is_superuser=user_data.is_superuser
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return UserResponse(
        success=True,
        message="User created successfully",
        user=UserSchema.from_orm(db_user)
    )


@router.put("/{user_id}", response_model=UserSchema)
async def update_user_by_admin(
    user_id: UUID,
    user_update: AdminUserUpdate,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Update user by ID (admin only)
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if email is being changed
    if user_update.email and user_update.email != user.email:
        existing_user = await AuthService.get_user_by_email(db, user_update.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
    
    # Check if username is being changed
    if user_update.username and user_update.username != user.username:
        result = await db.execute(
            select(User).where(User.username == user_update.username)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Update fields
    update_data = user_update.dict(exclude_unset=True)
    
    # Handle password update if provided
    if "password" in update_data:
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
    
    user.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(user)
    
    return UserSchema.from_orm(user)


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user_by_admin(
    user_id: UUID,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Delete user by ID (admin only)
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Don't allow deleting yourself
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    db.delete(user)
    await db.commit()
    
    return MessageResponse(message="User deleted successfully")