from typing import Any, List, Optional, Dict
from uuid import UUID
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, desc

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

# Audit log storage (in production, this should be in database)
audit_log: List[Dict[str, Any]] = []

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
    
    # Log admin action
    log_admin_action(
        action="update_user",
        user_id=user.id,
        admin_id=current_user.id,
        details=update_data
    )
    
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

@router.get("/stats")
async def get_system_stats(
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Get system statistics (admin only)
    """
    # Total users
    total_query = select(func.count(User.id))
    total_result = await db.execute(total_query)
    total_users = total_result.scalar() or 0
    
    # Active users
    active_query = select(func.count(User.id)).where(User.is_active == True)
    active_result = await db.execute(active_query)
    active_users = active_result.scalar() or 0
    
    # Verified users
    verified_query = select(func.count(User.id)).where(User.is_verified == True)
    verified_result = await db.execute(verified_query)
    verified_users = verified_result.scalar() or 0
    
    # Superusers
    superuser_query = select(func.count(User.id)).where(User.is_superuser == True)
    superuser_result = await db.execute(superuser_query)
    superusers = superuser_result.scalar() or 0
    
    # Users registered in last 7 days
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_users_query = select(func.count(User.id)).where(User.created_at >= week_ago)
    new_users_result = await db.execute(new_users_query)
    new_users_this_week = new_users_result.scalar() or 0
    
    # Users logged in last 24 hours
    day_ago = datetime.utcnow() - timedelta(days=1)
    active_today_query = select(func.count(User.id)).where(
        and_(User.last_login_at >= day_ago, User.last_login_at is not None)
    )
    active_today_result = await db.execute(active_today_query)
    active_today = active_today_result.scalar() or 0
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "verified_users": verified_users,
        "superusers": superusers,
        "inactive_users": total_users - active_users,
        "unverified_users": total_users - verified_users,
        "new_users_this_week": new_users_this_week,
        "active_today": active_today
    }

@router.get("/recent-registrations", response_model=List[UserSchema])
async def get_recent_registrations(
    limit: int = Query(10, ge=1, le=100, description="Number of users to return"),
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Get recently registered users (admin only)
    """
    query = select(User).order_by(desc(User.created_at)).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()
    
    return [UserSchema.from_orm(user) for user in users]

@router.get("/audit-log")
async def get_audit_log(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_superuser)
) -> Any:
    """
    Get audit log of admin actions (admin only)
    """
    # Return paginated audit log
    return {
        "total": len(audit_log),
        "items": audit_log[skip:skip + limit]
    }

def log_admin_action(
    action: str,
    user_id: UUID,
    admin_id: UUID,
    details: Optional[Dict[str, Any]] = None
):
    """
    Helper function to log admin actions
    """
    audit_log.append({
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "user_id": str(user_id),
        "admin_id": str(admin_id),
        "details": details or {}
    })

@router.post("/users/{user_id}/reset-password", response_model=MessageResponse)
async def reset_user_password_admin(
    user_id: UUID,
    new_password: str = Query(..., min_length=8, max_length=128, description="New password for the user"),
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Reset user password (admin only)
    """
    user = await AuthService.get_user_by_id(db, user_id)
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
    
    # Reset password
    user.hashed_password = AuthService.get_password_hash(new_password)
    user.password_reset_token = None
    user.password_reset_at = None
    
    await db.commit()
    
    # Log admin action
    log_admin_action(
        action="reset_password",
        user_id=user.id,
        admin_id=current_user.id
    )
    
    return MessageResponse(message="Password reset successfully")

@router.get("/users/export")
async def export_users(
    format: str = Query("csv", description="Export format: csv or json"),
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Export all users to CSV or JSON (admin only)
    """
    # Get all users
    result = await db.execute(select(User))
    users = result.scalars().all()
    
    if format == "json":
        # Return JSON format
        return {
            "export_date": datetime.utcnow().isoformat(),
            "total_users": len(users),
            "users": [
                {
                    "id": str(user.id),
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.full_name,
                    "is_active": user.is_active,
                    "is_superuser": user.is_superuser,
                    "is_verified": user.is_verified,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None
                }
                for user in users
            ]
        }
    else:
        # Return CSV format
        import csv
        import io
        from fastapi.responses import Response
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "ID", "Email", "Username", "Full Name", 
            "Active", "Superuser", "Verified", 
            "Created At", "Last Login"
        ])
        
        # Write data
        for user in users:
            writer.writerow([
                str(user.id),
                user.email,
                user.username or "",
                user.full_name or "",
                "Yes" if user.is_active else "No",
                "Yes" if user.is_superuser else "No",
                "Yes" if user.is_verified else "No",
                user.created_at.isoformat() if user.created_at else "",
                user.last_login_at.isoformat() if user.last_login_at else ""
            ])
        
        output.seek(0)
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=users_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )

@router.post("/users/import", response_model=MessageResponse)
async def import_users(
    users_data: List[Dict[str, Any]],
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Import users from JSON (admin only)
    """
    imported_count = 0
    skipped_count = 0
    errors = []
    
    for user_data in users_data:
        try:
            # Check if user already exists
            email = user_data.get("email")
            if not email:
                errors.append("Missing email in user data")
                continue
            
            existing_user = await AuthService.get_user_by_email(db, email)
            if existing_user:
                skipped_count += 1
                continue
            
            # Create new user
            password = user_data.get("password")
            if not password:
                # Generate random password if not provided
                password = SecurityService.generate_secure_password()
            
            hashed_password = AuthService.get_password_hash(password)
            
            new_user = User(
                email=email,
                hashed_password=hashed_password,
                username=user_data.get("username"),
                full_name=user_data.get("full_name"),
                is_active=user_data.get("is_active", True),
                is_superuser=user_data.get("is_superuser", False),
                is_verified=user_data.get("is_verified", False)
            )
            
            db.add(new_user)
            imported_count += 1
            
        except Exception as e:
            errors.append(f"Error importing user {email}: {str(e)}")
    
    await db.commit()
    
    # Log admin action
    log_admin_action(
        action="import_users",
        user_id=current_user.id,  # Using admin's ID since it's a bulk operation
        admin_id=current_user.id,
        details={
            "imported": imported_count,
            "skipped": skipped_count,
            "errors": len(errors)
        }
    )
    
    return MessageResponse(
        message=f"Import completed: {imported_count} imported, {skipped_count} skipped, {len(errors)} errors"
    )

@router.post("/users/bulk-activate", response_model=MessageResponse)
async def bulk_activate_users(
    user_ids: List[UUID],
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Bulk activate multiple users (admin only)
    """
    if not user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user IDs provided"
        )
    
    # Get users
    result = await db.execute(
        select(User).where(User.id.in_(user_ids))
    )
    users = result.scalars().all()
    
    activated_count = 0
    for user in users:
        if not user.is_active:
            user.is_active = True
            activated_count += 1
    
    await db.commit()
    
    # Log admin action
    log_admin_action(
        action="bulk_activate",
        user_id=current_user.id,  # Using admin's ID for bulk operation
        admin_id=current_user.id,
        details={
            "user_ids": [str(uid) for uid in user_ids],
            "activated_count": activated_count
        }
    )
    
    return MessageResponse(
        message=f"Successfully activated {activated_count} users"
    )

@router.post("/users/bulk-deactivate", response_model=MessageResponse)
async def bulk_deactivate_users(
    user_ids: List[UUID],
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Bulk deactivate multiple users (admin only)
    """
    if not user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user IDs provided"
        )
    
    # Prevent admin from deactivating themselves
    if current_user.id in user_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot deactivate your own account"
        )
    
    # Get users
    result = await db.execute(
        select(User).where(User.id.in_(user_ids))
    )
    users = result.scalars().all()
    
    deactivated_count = 0
    for user in users:
        if user.is_active:
            user.is_active = False
            deactivated_count += 1
    
    await db.commit()
    
    # Log admin action
    log_admin_action(
        action="bulk_deactivate",
        user_id=current_user.id,  # Using admin's ID for bulk operation
        admin_id=current_user.id,
        details={
            "user_ids": [str(uid) for uid in user_ids],
            "deactivated_count": deactivated_count
        }
    )
    
    return MessageResponse(
        message=f"Successfully deactivated {deactivated_count} users"
    )

@router.get("/users/{user_id}/sessions")
async def get_user_sessions(
    user_id: UUID,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Get active sessions for a user (admin only)
    Note: This is a placeholder - actual implementation would require session tracking
    """
    user = await AuthService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # In a real implementation, you would track sessions in a separate table
    # For now, return basic session info based on last login
    sessions = []
    if user.last_login_at:
        sessions.append({
            "session_id": str(user_id) + "-session-1",  # Mock session ID
            "created_at": user.last_login_at.isoformat(),
            "last_activity": user.last_login_at.isoformat(),
            "ip_address": "Unknown",
            "user_agent": "Unknown",
            "is_current": False
        })
    
    return {
        "user_id": str(user_id),
        "total_sessions": len(sessions),
        "sessions": sessions
    }

@router.delete("/users/{user_id}/sessions", response_model=MessageResponse)
async def invalidate_user_sessions(
    user_id: UUID,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Invalidate all sessions for a user (admin only)
    Note: This is a placeholder - actual implementation would require session tracking
    """
    user = await AuthService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # In a real implementation, you would:
    # 1. Delete all refresh tokens for the user
    # 2. Blacklist all active access tokens
    # 3. Clear any session data in cache/database
    
    # For now, we'll just log the action
    log_admin_action(
        action="invalidate_sessions",
        user_id=user.id,
        admin_id=current_user.id
    )
    
    return MessageResponse(
        message=f"All sessions for user {user.email} have been invalidated"
    )