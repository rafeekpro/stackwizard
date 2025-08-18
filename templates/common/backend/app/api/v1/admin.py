from typing import Any, List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_

from app.core.dependencies import get_current_superuser, get_async_db
from app.models.user import User
from app.schemas.user import (
    User as UserSchema,
    AdminUserCreate,
    AdminUserUpdate,
    UserResponse,
    MessageResponse
)
from app.services.auth import AuthService, SecurityService

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users", response_model=List[UserSchema])
async def get_all_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
    search: Optional[str] = Query(None, description="Search in email, username, or full_name"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_superuser: Optional[bool] = Query(None, description="Filter by superuser status"),
    is_verified: Optional[bool] = Query(None, description="Filter by verified status"),
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
    
    # Status filters
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    
    if is_superuser is not None:
        query = query.where(User.is_superuser == is_superuser)
    
    if is_verified is not None:
        query = query.where(User.is_verified == is_verified)
    
    # Apply pagination
    query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    return [UserSchema.from_orm(user) for user in users]

@router.get("/users/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Get user statistics (admin only)
    """
    # Total users
    total_query = select(func.count(User.id))
    total_result = await db.execute(total_query)
    total_users = total_result.scalar()
    
    # Active users
    active_query = select(func.count(User.id)).where(User.is_active == True)
    active_result = await db.execute(active_query)
    active_users = active_result.scalar()
    
    # Verified users
    verified_query = select(func.count(User.id)).where(User.is_verified == True)
    verified_result = await db.execute(verified_query)
    verified_users = verified_result.scalar()
    
    # Superusers
    superuser_query = select(func.count(User.id)).where(User.is_superuser == True)
    superuser_result = await db.execute(superuser_query)
    superusers = superuser_result.scalar()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "verified_users": verified_users,
        "superusers": superusers,
        "inactive_users": total_users - active_users,
        "unverified_users": total_users - verified_users
    }

@router.get("/users/{user_id}", response_model=UserSchema)
async def get_user_by_id(
    user_id: UUID,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Get specific user by ID (admin only)
    """
    user = await AuthService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserSchema.from_orm(user)

@router.post("/users", response_model=UserResponse)
async def create_user_admin(
    user_data: AdminUserCreate,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Create new user as admin
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
        is_superuser=user_data.is_superuser,
        is_verified=user_data.is_verified,
        email_verification_token=None if user_data.is_verified else AuthService.create_email_verification_token()
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return UserResponse(
        user=UserSchema.from_orm(db_user),
        message="User created successfully"
    )

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user_admin(
    user_id: UUID,
    user_update: AdminUserUpdate,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Update user as admin
    """
    user = await AuthService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from modifying themselves to lose superuser status
    if user.id == current_user.id and user_update.is_superuser is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot remove superuser status from your own account"
        )
    
    # Check if email is being changed and if it's already taken
    if user_update.email and user_update.email != user.email:
        existing_user = await AuthService.get_user_by_email(db, user_update.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
    
    # Check if username is being changed and if it's already taken
    if user_update.username and user_update.username != user.username:
        result = await db.execute(
            select(User).where(
                and_(User.username == user_update.username, User.id != user_id)
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Update user fields
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(user, field):
            setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    
    return UserResponse(
        user=UserSchema.from_orm(user),
        message="User updated successfully"
    )

@router.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user_admin(
    user_id: UUID,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Delete user as admin (soft delete - deactivate)
    """
    user = await AuthService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete your own account"
        )
    
    # Soft delete - deactivate user
    user.is_active = False
    await db.commit()
    
    return MessageResponse(message="User deactivated successfully")

@router.post("/users/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: UUID,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Activate deactivated user (admin only)
    """
    user = await AuthService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = True
    await db.commit()
    await db.refresh(user)
    
    return UserResponse(
        user=UserSchema.from_orm(user),
        message="User activated successfully"
    )

@router.post("/users/{user_id}/make-superuser", response_model=UserResponse)
async def make_superuser(
    user_id: UUID,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Grant superuser privileges (admin only)
    """
    user = await AuthService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_superuser:
        return UserResponse(
            user=UserSchema.from_orm(user),
            message="User is already a superuser"
        )
    
    user.is_superuser = True
    await db.commit()
    await db.refresh(user)
    
    return UserResponse(
        user=UserSchema.from_orm(user),
        message="User granted superuser privileges"
    )

@router.post("/users/{user_id}/remove-superuser", response_model=UserResponse)
async def remove_superuser(
    user_id: UUID,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Remove superuser privileges (admin only)
    """
    user = await AuthService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from removing superuser from themselves
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot remove superuser status from your own account"
        )
    
    user.is_superuser = False
    await db.commit()
    await db.refresh(user)
    
    return UserResponse(
        user=UserSchema.from_orm(user),
        message="Superuser privileges removed"
    )

@router.post("/users/{user_id}/verify-email", response_model=UserResponse)
async def verify_user_email_admin(
    user_id: UUID,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Manually verify user email (admin only)
    """
    user = await AuthService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_verified:
        return UserResponse(
            user=UserSchema.from_orm(user),
            message="User email is already verified"
        )
    
    user.is_verified = True
    user.email_verified_at = datetime.utcnow()
    user.email_verification_token = None
    await db.commit()
    await db.refresh(user)
    
    return UserResponse(
        user=UserSchema.from_orm(user),
        message="User email verified successfully"
    )