"""
Test User model to ensure all required fields are present
Following TDD - these tests should be written BEFORE implementation
"""
import uuid
from datetime import datetime
import pytest
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.auth import AuthService


class TestUserModel:
    """Test User model has all required fields and behaviors"""
    
    def test_user_table_exists(self, db: Session):
        """Test that users table exists in database"""
        inspector = inspect(db.bind)
        assert 'users' in inspector.get_table_names()
    
    def test_user_has_uuid_id(self, db: Session):
        """Test that User model has UUID as primary key"""
        user = User(
            email="test@example.com",
            hashed_password="hashed",
            username="testuser"
        )
        db.add(user)
        db.commit()
        
        assert user.id is not None
        assert isinstance(user.id, uuid.UUID)
    
    def test_user_has_required_fields(self, db: Session):
        """Test that User model has all required fields"""
        user = User(
            email="test@example.com",
            hashed_password=AuthService.get_password_hash("password"),
            username="testuser",
            full_name="Test User"
        )
        db.add(user)
        db.commit()
        
        # Required fields
        assert user.email == "test@example.com"
        assert user.hashed_password is not None
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        
        # Default values
        assert user.is_active is True  # Should default to True
        assert user.is_superuser is False  # Should default to False
        assert user.is_verified is False  # Should default to False
        
        # Timestamps
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
        assert user.last_login_at is None  # Should be None initially
        assert user.login_count == 0  # Should default to 0
    
    def test_user_email_is_unique(self, db: Session):
        """Test that email field has unique constraint"""
        user1 = User(
            email="unique@example.com",
            hashed_password="hash1",
            username="user1"
        )
        db.add(user1)
        db.commit()
        
        user2 = User(
            email="unique@example.com",  # Same email
            hashed_password="hash2",
            username="user2"
        )
        db.add(user2)
        
        with pytest.raises(Exception):  # Should raise integrity error
            db.commit()
    
    def test_user_username_is_unique(self, db: Session):
        """Test that username field has unique constraint"""
        user1 = User(
            email="user1@example.com",
            hashed_password="hash1",
            username="uniqueuser"
        )
        db.add(user1)
        db.commit()
        
        user2 = User(
            email="user2@example.com",
            hashed_password="hash2",
            username="uniqueuser"  # Same username
        )
        db.add(user2)
        
        with pytest.raises(Exception):  # Should raise integrity error
            db.commit()
    
    def test_user_password_is_hashed(self, db: Session):
        """Test that password is properly hashed"""
        plain_password = "TestPassword123!"
        user = User(
            email="hashed@example.com",
            hashed_password=AuthService.get_password_hash(plain_password),
            username="hasheduser"
        )
        db.add(user)
        db.commit()
        
        # Password should be hashed, not plain
        assert user.hashed_password != plain_password
        assert len(user.hashed_password) > 50  # Bcrypt hashes are long
        
        # Should be able to verify the password
        assert AuthService.verify_password(plain_password, user.hashed_password) is True
        assert AuthService.verify_password("WrongPassword", user.hashed_password) is False
    
    def test_user_update_timestamp(self, db: Session):
        """Test that updated_at changes when user is modified"""
        user = User(
            email="timestamp@example.com",
            hashed_password="hash",
            username="timestampuser"
        )
        db.add(user)
        db.commit()
        
        original_updated = user.updated_at
        
        # Update user
        user.full_name = "Updated Name"
        db.commit()
        
        # updated_at should have changed
        assert user.updated_at > original_updated
    
    def test_user_soft_delete_with_is_active(self, db: Session):
        """Test that users can be soft-deleted using is_active flag"""
        user = User(
            email="soft@example.com",
            hashed_password="hash",
            username="softuser",
            is_active=True
        )
        db.add(user)
        db.commit()
        
        assert user.is_active is True
        
        # Soft delete
        user.is_active = False
        db.commit()
        
        assert user.is_active is False
        
        # User should still exist in database
        found_user = db.query(User).filter_by(email="soft@example.com").first()
        assert found_user is not None
        assert found_user.is_active is False
    
    def test_user_login_tracking(self, db: Session):
        """Test that login count and last_login_at can be tracked"""
        user = User(
            email="login@example.com",
            hashed_password="hash",
            username="loginuser",
            login_count=0
        )
        db.add(user)
        db.commit()
        
        assert user.login_count == 0
        assert user.last_login_at is None
        
        # Simulate login
        user.login_count += 1
        user.last_login_at = datetime.utcnow()
        db.commit()
        
        assert user.login_count == 1
        assert user.last_login_at is not None
        assert isinstance(user.last_login_at, datetime)