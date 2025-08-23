from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.dependencies import get_current_active_user, get_current_user
from app.db.database import get_async_db
from app.models.user import User
from app.schemas.user import (
    Token, TokenWithUser, UserLogin, UserRegister, User as UserSchema,
    PasswordResetRequest, PasswordReset, MessageResponse,
    UserResponse
)
from app.services.auth import AuthService, SecurityService

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/login", response_model=TokenWithUser)
async def login(
    db: AsyncSession = Depends(get_async_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await AuthService.authenticate_user(
        db, 
        email=form_data.username,  # OAuth2 uses 'username' field but we use email
        password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    await AuthService.update_last_login(db, user)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Create access token with scopes
    scopes = ["read", "write"]
    if user.is_superuser:
        scopes.append("admin")
    
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
        scopes=scopes
    )
    
    # Create refresh token
    refresh_token = AuthService.create_refresh_token(
        data={"sub": str(user.id)}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "refresh_token": refresh_token,
        "user": {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "is_superuser": user.is_superuser,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }
    }

@router.post("/login-json", response_model=TokenWithUser)
async def login_json(
    user_credentials: UserLogin,
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    JSON login endpoint (alternative to OAuth2 form)
    """
    user = await AuthService.authenticate_user(
        db, 
        email=user_credentials.email,
        password=user_credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Update last login
    await AuthService.update_last_login(db, user)
    
    # Determine token expiration based on remember_me
    if user_credentials.remember_me:
        access_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    else:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Create access token with scopes
    scopes = ["read", "write"]
    if user.is_superuser:
        scopes.append("admin")
    
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
        scopes=scopes
    )
    
    # Create refresh token
    refresh_token = AuthService.create_refresh_token(
        data={"sub": str(user.id)}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": int(access_token_expires.total_seconds()),
        "refresh_token": refresh_token,
        "user": {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "is_superuser": user.is_superuser,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }
    }

@router.post("/register", response_model=TokenWithUser)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Register new user
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
    email_verification_token = AuthService.create_email_verification_token()
    
    # Generate username from email if not provided
    username = user_data.username or user_data.email.split('@')[0]
    
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        username=username,
        full_name=user_data.full_name,
        email_verification_token=email_verification_token,
        is_active=True,
        is_verified=False  # Email verification required
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    # TODO: Send email verification email here
    # await send_email_verification(db_user.email, email_verification_token)
    
    # Create access token for immediate login
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Create access token with scopes
    scopes = ["read", "write"]
    if db_user.is_superuser:
        scopes.append("admin")
    
    access_token = AuthService.create_access_token(
        data={"sub": str(db_user.id)},
        expires_delta=access_token_expires,
        scopes=scopes
    )
    
    # Create refresh token
    refresh_token = AuthService.create_refresh_token(
        data={"sub": str(db_user.id)}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "refresh_token": refresh_token,
        "user": {
            "id": str(db_user.id),
            "email": db_user.email,
            "username": db_user.username,
            "full_name": db_user.full_name,
            "is_superuser": db_user.is_superuser,
            "is_active": db_user.is_active,
            "created_at": db_user.created_at.isoformat() if db_user.created_at else None,
            "updated_at": db_user.updated_at.isoformat() if db_user.updated_at else None
        },
        "message": "User registered successfully. Please check your email to verify your account."
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Refresh access token using refresh token
    """
    try:
        payload = AuthService.verify_token(refresh_token)
        if not payload or not payload.user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user
        user = await AuthService.get_user_by_id(db, payload.user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        scopes = ["read", "write"]
        if user.is_superuser:
            scopes.append("admin")
        
        access_token = AuthService.create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires,
            scopes=scopes
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Logout current user (client should discard tokens)
    """
    # In a more complete implementation, you might want to blacklist the token
    # For now, we just confirm the logout action
    return MessageResponse(message="Successfully logged out")

@router.post("/password-recovery", response_model=MessageResponse)
async def recover_password(
    reset_request: PasswordResetRequest,
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Password Recovery: Send password reset email
    """
    email = reset_request.email
    
    user = await AuthService.get_user_by_email(db, str(email))
    if not user:
        # Don't reveal if email exists or not for security
        return MessageResponse(
            message="Password recovery email sent"
        )
    
    if not user.is_active:
        return MessageResponse(
            message="Password recovery email sent"
        )
    
    # Generate password reset token
    reset_token = AuthService.create_password_reset_token()
    user.password_reset_token = reset_token
    user.password_reset_at = datetime.utcnow()
    
    await db.commit()
    
    # TODO: Send password reset email here
    # await send_password_reset_email(user.email, reset_token)
    
    return MessageResponse(
        message="Password recovery email sent"
    )

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    reset_data: PasswordReset,
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Reset password using reset token
    """
    user = await AuthService.get_user_by_reset_token(db, reset_data.token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Validate password strength
    is_valid, errors = SecurityService.validate_password_strength(reset_data.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Password does not meet requirements", "errors": errors}
        )
    
    # Update password and clear reset token
    user.hashed_password = AuthService.get_password_hash(reset_data.new_password)
    user.password_reset_token = None
    user.password_reset_at = None
    
    await db.commit()
    
    return MessageResponse(message="Password reset successfully")

@router.get("/verify-token", response_model=UserSchema)
async def verify_token(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Verify token and return current user info
    """
    return UserSchema.from_orm(current_user)