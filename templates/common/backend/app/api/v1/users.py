from typing import Any, List, Optional, Dict
from uuid import UUID
from datetime import datetime, timezone
import json

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func

from app.core.dependencies import (
    get_current_active_user,
    get_current_verified_user,
    get_current_superuser,
    get_async_db
)
from app.models.user import User
from app.schemas.user import (
    User as UserSchema,
    UserCreate,
    UserUpdate,
    UserPasswordUpdate,
    UserResponse,
    MessageResponse,
    AdminUserUpdate,
    AdminUserCreate
)
from app.services.auth import AuthService, SecurityService

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get current user information
    """
    return UserSchema.from_orm(current_user)

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Update current user information
    """
    # Check if email is being changed and if it's already taken
    if user_update.email and user_update.email != current_user.email:
        existing_user = await AuthService.get_user_by_email(db, user_update.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        # If email is changed, user needs to verify it again
        current_user.is_verified = False
        current_user.email_verification_token = AuthService.create_email_verification_token()
        # TODO: Send verification email
    
    # Check if username is being changed and if it's already taken
    if user_update.username and user_update.username != current_user.username:
        result = await db.execute(
            select(User).where(User.username == user_update.username)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Update user fields
    update_data = user_update.dict(exclude_unset=True)
    
    # Handle password update separately for security
    if "password" in update_data:
        # Validate password strength
        is_valid, errors = SecurityService.validate_password_strength(update_data["password"])
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Password does not meet requirements", "errors": errors}
            )
        
        current_user.hashed_password = AuthService.get_password_hash(update_data["password"])
        del update_data["password"]
    
    # Update other fields
    for field, value in update_data.items():
        if hasattr(current_user, field):
            setattr(current_user, field, value)
    
    await db.commit()
    await db.refresh(current_user)
    
    message = "User updated successfully"
    if user_update.email and user_update.email != current_user.email:
        message += ". Please verify your new email address."
    
    return UserResponse(
        user=UserSchema.from_orm(current_user),
        message=message
    )

@router.put("/me/password", response_model=MessageResponse)
async def update_current_user_password(
    password_update: UserPasswordUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Update current user password
    """
    # Verify current password
    if not AuthService.verify_password(
        password_update.current_password, 
        current_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Check if new password is different from current
    if AuthService.verify_password(
        password_update.new_password, 
        current_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    # Validate new password strength
    is_valid, errors = SecurityService.validate_password_strength(password_update.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Password does not meet requirements", "errors": errors}
        )
    
    # Update password
    current_user.hashed_password = AuthService.get_password_hash(password_update.new_password)
    await db.commit()
    
    return MessageResponse(message="Password updated successfully")

@router.delete("/me", response_model=MessageResponse)
async def deactivate_current_user(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Deactivate current user account
    """
    if current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser accounts cannot be deactivated"
        )
    
    current_user.is_active = False
    await db.commit()
    
    return MessageResponse(message="Account deactivated successfully")

@router.get("/me/profile", response_model=UserSchema)
async def get_user_profile(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get detailed user profile (same as /me but more explicit)
    """
    return UserSchema.from_orm(current_user)

@router.get("/me/statistics", response_model=Dict[str, Any])
async def get_user_statistics(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """Get current user statistics"""
    from app.models.item import Item
    from datetime import timezone
    
    # Get user's items count
    items_result = await db.execute(
        select(func.count(Item.id)).where(Item.owner_id == current_user.id)
    )
    items_count = items_result.scalar() or 0
    
    # Calculate account age - use timezone-aware datetime
    now = datetime.now(timezone.utc)
    account_age = now - current_user.created_at
    
    return {
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

@router.get("/me/export")
async def export_user_data(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """Export all user data as JSON"""
    from app.models.item import Item
    from datetime import timezone
    
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

# Email verification endpoints
@router.post("/verify-email/{token}", response_model=MessageResponse)
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Verify email address using verification token
    """
    user = await AuthService.get_user_by_verification_token(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    if user.is_verified:
        return MessageResponse(message="Email already verified")
    
    # Verify email
    user.is_verified = True
    user.email_verified_at = datetime.utcnow()
    user.email_verification_token = None
    
    await db.commit()
    
    return MessageResponse(message="Email verified successfully")

# Admin endpoints for user management
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
        is_superuser=user_data.is_superuser,
        email_verification_token=None if user_data.is_verified else AuthService.create_email_verification_token()
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return UserResponse(
        user=UserSchema.from_orm(db_user),
        message="User created successfully"
    )

@router.put("/{user_id}", response_model=UserSchema)
async def update_user_by_admin(
    user_id: UUID,
    user_update: AdminUserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Update user by ID (admin only)
    """
    # Check if current user is admin
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Get user to update
    result = await db.execute(select(User).where(User.id == user_id))
    user_to_update = result.scalar_one_or_none()
    
    if not user_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user fields
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user_to_update, field, value)
    
    user_to_update.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user_to_update)
    
    return UserSchema.from_orm(user_to_update)

@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user_by_admin(
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Delete user by ID (admin only)
    """
    # Check if current user is admin
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Prevent deleting yourself
    if str(current_user.id) == str(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Get user to delete
    result = await db.execute(select(User).where(User.id == user_id))
    user_to_delete = result.scalar_one_or_none()
    
    if not user_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Soft delete user (deactivate)
    user_to_delete.is_active = False
    await db.commit()
    
    return MessageResponse(message="User deleted successfully")

@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification_email(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Resend email verification
    """
    if current_user.is_verified:
        return MessageResponse(message="Email already verified")
    
    # Generate new verification token
    current_user.email_verification_token = AuthService.create_email_verification_token()
    await db.commit()
    
    # TODO: Send verification email
    # await send_email_verification(current_user.email, current_user.email_verification_token)
    
    return MessageResponse(message="Verification email sent")