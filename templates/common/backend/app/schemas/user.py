from typing import Optional, Union
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from uuid import UUID

# Base user schema
class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

# User creation schema (registration)
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=255)
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

# User update schema
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=8, max_length=128)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

# Password update schema
class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

# Base schema for database models
class UserInDBBase(UserBase):
    id: UUID
    is_verified: bool
    login_count: int
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Public user schema (returned to clients)
class User(UserInDBBase):
    pass

# Internal user schema (with hashed password)
class UserInDB(UserInDBBase):
    hashed_password: str
    password_reset_token: Optional[str] = None
    password_reset_at: Optional[datetime] = None
    email_verification_token: Optional[str] = None
    email_verified_at: Optional[datetime] = None

# Authentication schemas
class UserSchema(BaseModel):
    id: str
    email: str
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_superuser: bool = False
    is_active: bool = True
    is_verified: bool = False
    login_count: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None

class TokenWithUser(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None
    user: Optional[UserSchema] = None
    message: Optional[str] = None

class RegisterResponse(BaseModel):
    user: UserSchema
    message: str

class TokenData(BaseModel):
    user_id: Optional[UUID] = None
    scopes: list[str] = []

class RefreshToken(BaseModel):
    refresh_token: str

# Login schemas
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    username: Optional[str] = Field(None, max_length=50)
    full_name: Optional[str] = Field(None, max_length=255)
    
    @validator('username', pre=True)
    def empty_str_to_none(cls, v):
        if v == '':
            return None
        if v and len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

# Password recovery schemas
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

# Email verification schemas
class EmailVerificationRequest(BaseModel):
    email: EmailStr

class EmailVerification(BaseModel):
    token: str

# Response schemas
class UserResponse(BaseModel):
    user: User
    message: str

class MessageResponse(BaseModel):
    message: str

# Admin schemas
class AdminUserCreate(UserCreate):
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

class AdminUserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None