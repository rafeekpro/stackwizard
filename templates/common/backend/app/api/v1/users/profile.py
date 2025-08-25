"""
User Profile Endpoints
Handles current user profile operations
"""
from typing import Any
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.dependencies import (
    get_current_active_user,
    get_async_db
)
from app.models.user import User
from app.schemas.user import (
    User as UserSchema,
    UserUpdate,
    UserPasswordUpdate,
    UserResponse,
    MessageResponse
)
from app.services.auth import AuthService, SecurityService

router = APIRouter()


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
        success=True,
        message=message,
        user=UserSchema.from_orm(current_user)
    )


@router.put("/me/password", response_model=MessageResponse)
async def update_password(
    password_update: UserPasswordUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Update current user password
    """
    # Verify current password
    if not AuthService.verify_password(password_update.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Validate new password strength
    is_valid, errors = SecurityService.validate_password_strength(password_update.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "New password does not meet requirements", "errors": errors}
        )
    
    # Check if new password is different from current
    if AuthService.verify_password(password_update.new_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    # Update password
    current_user.hashed_password = AuthService.get_password_hash(password_update.new_password)
    current_user.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    
    return MessageResponse(message="Password updated successfully")


@router.delete("/me", response_model=MessageResponse)
async def deactivate_account(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Deactivate current user account
    """
    current_user.is_active = False
    current_user.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    
    return MessageResponse(message="Account deactivated successfully")