"""
Refactored Users API endpoints using Service Layer
Clean separation of concerns with business logic in UserService
"""
from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import (
    get_current_active_user,
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
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get current user information"""
    return UserSchema.from_orm(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """Update current user information"""
    user = await UserService.update_user(db, current_user, user_update)
    
    message = "User updated successfully"
    if user_update.email and user_update.email != current_user.email:
        message += ". Please verify your new email address."
    
    return UserResponse(
        message=message,
        user=UserSchema.from_orm(user)
    )


@router.put("/me/password", response_model=MessageResponse)
async def change_password(
    password_update: UserPasswordUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """Change current user's password"""
    await UserService.update_password(db, current_user, password_update)
    return MessageResponse(message="Password updated successfully")


@router.delete("/me", response_model=MessageResponse)
async def delete_current_user(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """Deactivate current user account"""
    await UserService.delete_user(db, current_user, soft_delete=True)
    return MessageResponse(message="Account deactivated successfully")


@router.get("/me/statistics", response_model=dict)
async def get_user_statistics(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """Get current user's statistics"""
    stats = await UserService.get_user_statistics(db, current_user)
    return stats


@router.get("/me/export")
async def export_user_data(
    include_items: bool = Query(True, description="Include user's items in export"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """Export all user data (GDPR compliance)"""
    export_data = await UserService.export_user_data(db, current_user, include_items)
    
    from datetime import datetime, timezone
    return JSONResponse(
        content=export_data,
        headers={
            "Content-Disposition": f"attachment; filename=user_data_{current_user.id}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        }
    )


# Admin endpoints
@router.get("/", response_model=List[UserSchema])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search in email, username, or full name"),
    is_active: Optional[bool] = Query(None),
    is_verified: Optional[bool] = Query(None),
    is_superuser: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """List all users (admin only)"""
    users = await UserService.list_users(
        db,
        skip=skip,
        limit=limit,
        search=search,
        is_active=is_active,
        is_verified=is_verified,
        is_superuser=is_superuser
    )
    return [UserSchema.from_orm(user) for user in users]


@router.get("/{user_id}", response_model=UserSchema)
async def get_user_by_id(
    user_id: UUID,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """Get user by ID (admin only)"""
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserSchema.from_orm(user)


@router.post("/", response_model=UserResponse)
async def create_user(
    user_create: AdminUserCreate,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """Create a new user (admin only)"""
    user = await UserService.create_user(
        db,
        user_create,
        is_verified=user_create.is_verified,
        is_superuser=user_create.is_superuser
    )
    
    return UserResponse(
        message="User created successfully",
        user=UserSchema.from_orm(user)
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_update: AdminUserUpdate,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """Update user (admin only)"""
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    updated_user = await UserService.update_user(db, user, user_update)
    
    return UserResponse(
        message="User updated successfully",
        user=UserSchema.from_orm(updated_user)
    )


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: UUID,
    permanent: bool = Query(False, description="Permanently delete user"),
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """Delete user (admin only)"""
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    await UserService.delete_user(db, user, soft_delete=not permanent)
    
    message = "User permanently deleted" if permanent else "User deactivated"
    return MessageResponse(message=message)


@router.post("/{user_id}/verify-email", response_model=MessageResponse)
async def verify_user_email(
    user_id: UUID,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """Manually verify user's email (admin only)"""
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_verified:
        return MessageResponse(message="User email is already verified")
    
    await UserService.verify_email(db, user)
    return MessageResponse(message="User email verified successfully")


@router.post("/{user_id}/reset-password", response_model=MessageResponse)
async def admin_reset_password(
    user_id: UUID,
    new_password: str,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """Reset user's password (admin only)"""
    from app.services.auth import AuthService, SecurityService
    
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Validate password strength
    is_valid, errors = SecurityService.validate_password_strength(new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Password does not meet requirements", "errors": errors}
        )
    
    # Update password
    user.hashed_password = AuthService.get_password_hash(new_password)
    from datetime import datetime, timezone
    user.password_changed_at = datetime.now(timezone.utc)
    
    await db.commit()
    
    return MessageResponse(message="Password reset successfully")