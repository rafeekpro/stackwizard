"""
Test Pydantic schemas for User
Following TDD - write tests first, then implementation
"""
import uuid
from datetime import datetime
import pytest
from pydantic import ValidationError

from app.schemas.user import (
    UserCreate, UserUpdate, UserInDB, User as UserSchema,
    Token, TokenData, UserPasswordUpdate, PasswordReset
)


class TestUserSchemas:
    """Test all User-related Pydantic schemas"""
    
    def test_user_create_schema(self):
        """Test UserCreate schema validation"""
        # Valid user creation
        user_data = {
            "email": "test@example.com",
            "password": "ValidPass123!",
            "username": "testuser",
            "full_name": "Test User"
        }
        user = UserCreate(**user_data)
        assert user.email == "test@example.com"
        assert user.password == "ValidPass123!"
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        
        # Optional fields
        minimal_user = UserCreate(
            email="minimal@example.com",
            password="MinimalPass123!"
        )
        assert minimal_user.email == "minimal@example.com"
        assert minimal_user.username is None  # Optional
        assert minimal_user.full_name is None  # Optional
    
    def test_user_create_email_validation(self):
        """Test email validation in UserCreate"""
        # Invalid email should raise error
        with pytest.raises(ValidationError):
            UserCreate(email="not-an-email", password="Pass123!")
        
        # Empty email should raise error
        with pytest.raises(ValidationError):
            UserCreate(email="", password="Pass123!")
    
    def test_user_create_password_validation(self):
        """Test password validation in UserCreate"""
        # Too short password
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="test@example.com", password="short")
        assert "at least 8 characters" in str(exc_info.value).lower()
        
        # No uppercase
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="test@example.com", password="lowercase123!")
        assert "uppercase" in str(exc_info.value).lower()
        
        # No number
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="test@example.com", password="NoNumbers!")
        assert "number" in str(exc_info.value).lower()
        
        # Valid password should pass
        user = UserCreate(email="test@example.com", password="ValidPass123!")
        assert user.password == "ValidPass123!"
    
    def test_user_update_schema(self):
        """Test UserUpdate schema for partial updates"""
        # All fields optional
        empty_update = UserUpdate()
        assert empty_update.email is None
        assert empty_update.username is None
        assert empty_update.full_name is None
        assert empty_update.password is None
        assert empty_update.is_active is None
        assert empty_update.is_verified is None
        assert empty_update.is_superuser is None
        
        # Partial update
        partial_update = UserUpdate(full_name="New Name", is_active=False)
        assert partial_update.full_name == "New Name"
        assert partial_update.is_active is False
        assert partial_update.email is None  # Not updated
    
    def test_user_schema_response(self):
        """Test UserSchema for API responses"""
        user_id = uuid.uuid4()
        now = datetime.utcnow()
        
        user_data = {
            "id": user_id,
            "email": "response@example.com",
            "username": "responseuser",
            "full_name": "Response User",
            "is_active": True,
            "is_superuser": False,
            "is_verified": True,
            "created_at": now,
            "updated_at": now,
            "last_login_at": None,
            "login_count": 0
        }
        
        user = UserSchema(**user_data)
        assert user.id == user_id
        assert user.email == "response@example.com"
        assert user.username == "responseuser"
        assert user.full_name == "Response User"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.is_verified is True
        assert user.created_at == now
        assert user.updated_at == now
        assert user.last_login_at is None
        assert user.login_count == 0
    
    def test_user_in_db_schema(self):
        """Test UserInDB schema with hashed password"""
        user_id = uuid.uuid4()
        
        user_data = {
            "id": user_id,
            "email": "db@example.com",
            "username": "dbuser",
            "hashed_password": "$2b$12$hashedpassword",
            "full_name": "DB User",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "login_count": 5,
            "last_login_at": datetime.utcnow()
        }
        
        user = UserInDB(**user_data)
        assert user.hashed_password == "$2b$12$hashedpassword"
        assert user.login_count == 5
        assert user.last_login_at is not None
    
    def test_token_schema(self):
        """Test Token schema for JWT responses"""
        token_data = {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "expires_in": 3600
        }
        
        token = Token(**token_data)
        assert token.access_token == token_data["access_token"]
        assert token.refresh_token == token_data["refresh_token"]
        assert token.token_type == "bearer"
        assert token.expires_in == 3600
    
    def test_token_data_schema(self):
        """Test TokenData schema for decoded JWT"""
        # With user_id
        token_data = TokenData(sub="user-uuid-here")
        assert token_data.sub == "user-uuid-here"
        
        # Without user_id (should be None)
        empty_token = TokenData()
        assert empty_token.sub is None
    
    def test_password_change_schema(self):
        """Test UserPasswordUpdate schema for password updates"""
        pwd_change = UserPasswordUpdate(
            current_password="OldPass123!",
            new_password="NewPass123!"
        )
        assert pwd_change.current_password == "OldPass123!"
        assert pwd_change.new_password == "NewPass123!"
        
        # New password should also be validated
        with pytest.raises(ValidationError):
            UserPasswordUpdate(
                current_password="OldPass123!",
                new_password="weak"  # Too short
            )
    
    def test_password_reset_schema(self):
        """Test PasswordReset schema for forgot password"""
        # Request reset
        reset_request = PasswordReset(email="forgot@example.com")
        assert reset_request.email == "forgot@example.com"
        assert not hasattr(reset_request, 'token')
        assert not hasattr(reset_request, 'new_password')
        
        # Reset with token
        reset_with_token = PasswordReset(
            email="forgot@example.com",
            token="reset-token-here",
            new_password="NewPass123!"
        )
        assert reset_with_token.email == "forgot@example.com"
        assert reset_with_token.token == "reset-token-here"
        assert reset_with_token.new_password == "NewPass123!"