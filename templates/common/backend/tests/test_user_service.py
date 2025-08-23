"""
Tests for UserService
Following TDD approach - tests written before implementation
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.services.user_service import UserService
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserPasswordUpdate


@pytest.fixture
def mock_db():
    """Create a mock database session"""
    db = AsyncMock(spec=AsyncSession)
    return db


@pytest.fixture
def sample_user():
    """Create a sample user for testing"""
    user = User(
        id=uuid4(),
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password="hashed_password",
        is_active=True,
        is_verified=True,
        is_superuser=False,
        created_at=datetime.now(timezone.utc)
    )
    return user


@pytest.mark.asyncio
class TestUserService:
    """Test suite for UserService"""
    
    async def test_get_user_by_id_found(self, mock_db, sample_user):
        """Test getting user by ID when user exists"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await UserService.get_user_by_id(mock_db, sample_user.id)
        
        # Assert
        assert result == sample_user
        mock_db.execute.assert_called_once()
    
    async def test_get_user_by_id_not_found(self, mock_db):
        """Test getting user by ID when user doesn't exist"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await UserService.get_user_by_id(mock_db, uuid4())
        
        # Assert
        assert result is None
        mock_db.execute.assert_called_once()
    
    async def test_get_user_by_email_found(self, mock_db, sample_user):
        """Test getting user by email when user exists"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await UserService.get_user_by_email(mock_db, "test@example.com")
        
        # Assert
        assert result == sample_user
        mock_db.execute.assert_called_once()
    
    async def test_get_user_by_username_found(self, mock_db, sample_user):
        """Test getting user by username when user exists"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await UserService.get_user_by_username(mock_db, "testuser")
        
        # Assert
        assert result == sample_user
        mock_db.execute.assert_called_once()
    
    async def test_list_users_with_filters(self, mock_db):
        """Test listing users with various filters"""
        # Arrange
        users = [
            User(id=uuid4(), email="user1@example.com", username="user1"),
            User(id=uuid4(), email="user2@example.com", username="user2")
        ]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = users
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await UserService.list_users(
            mock_db,
            skip=0,
            limit=10,
            search="user",
            is_active=True
        )
        
        # Assert
        assert result == users
        mock_db.execute.assert_called_once()
    
    @patch('app.services.user_service.AuthService')
    @patch('app.services.user_service.SecurityService')
    async def test_create_user_success(self, mock_security, mock_auth, mock_db):
        """Test successful user creation"""
        # Arrange
        mock_security.validate_password_strength.return_value = (True, [])
        mock_auth.get_password_hash.return_value = "hashed_password"
        mock_auth.create_email_verification_token.return_value = "token123"
        
        # Mock database queries
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None  # No existing user
        mock_db.execute.return_value = mock_result
        
        user_create = UserCreate(
            email="new@example.com",
            username="newuser",
            password="SecurePass123!",
            full_name="New User"
        )
        
        # Act
        result = await UserService.create_user(mock_db, user_create)
        
        # Assert
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    @patch('app.services.user_service.UserService.get_user_by_email')
    async def test_create_user_email_exists(self, mock_get_email, mock_db):
        """Test user creation when email already exists"""
        # Arrange
        mock_get_email.return_value = User(email="existing@example.com")
        
        user_create = UserCreate(
            email="existing@example.com",
            username="newuser",
            password="SecurePass123!",
            full_name="New User"
        )
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await UserService.create_user(mock_db, user_create)
        
        assert exc_info.value.status_code == 400
        assert "Email already registered" in str(exc_info.value.detail)
    
    @patch('app.services.user_service.AuthService')
    @patch('app.services.user_service.SecurityService')
    async def test_update_user_success(self, mock_security, mock_auth, mock_db, sample_user):
        """Test successful user update"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None  # No conflicting user
        mock_db.execute.return_value = mock_result
        
        user_update = UserUpdate(
            full_name="Updated Name",
            username="updateduser"
        )
        
        # Act
        result = await UserService.update_user(mock_db, sample_user, user_update)
        
        # Assert
        assert sample_user.full_name == "Updated Name"
        assert sample_user.username == "updateduser"
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    @patch('app.services.user_service.UserService.get_user_by_email')
    async def test_update_user_email_conflict(self, mock_get_email, mock_db, sample_user):
        """Test user update when new email is already taken"""
        # Arrange
        mock_get_email.return_value = User(email="taken@example.com", id=uuid4())
        
        user_update = UserUpdate(email="taken@example.com")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await UserService.update_user(mock_db, sample_user, user_update)
        
        assert exc_info.value.status_code == 400
        assert "Email already in use" in str(exc_info.value.detail)
    
    @patch('app.services.user_service.AuthService')
    @patch('app.services.user_service.SecurityService')
    async def test_update_password_success(self, mock_security, mock_auth, mock_db, sample_user):
        """Test successful password update"""
        # Arrange
        mock_auth.verify_password.return_value = True
        mock_security.validate_password_strength.return_value = (True, [])
        mock_auth.get_password_hash.return_value = "new_hashed_password"
        
        password_update = UserPasswordUpdate(
            current_password="oldpassword",
            new_password="NewSecurePass123!"
        )
        
        # Act
        result = await UserService.update_password(mock_db, sample_user, password_update)
        
        # Assert
        assert sample_user.hashed_password == "new_hashed_password"
        assert sample_user.password_changed_at is not None
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    @patch('app.services.user_service.AuthService')
    async def test_update_password_wrong_current(self, mock_auth, mock_db, sample_user):
        """Test password update with wrong current password"""
        # Arrange
        mock_auth.verify_password.return_value = False
        
        password_update = UserPasswordUpdate(
            current_password="wrongpassword",
            new_password="NewSecurePass123!"
        )
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await UserService.update_password(mock_db, sample_user, password_update)
        
        assert exc_info.value.status_code == 400
        assert "Current password is incorrect" in str(exc_info.value.detail)
    
    async def test_delete_user_soft_delete(self, mock_db, sample_user):
        """Test soft delete of user"""
        # Act
        result = await UserService.delete_user(mock_db, sample_user, soft_delete=True)
        
        # Assert
        assert result is True
        assert sample_user.is_active is False
        assert sample_user.deleted_at is not None
        mock_db.commit.assert_called_once()
    
    async def test_delete_user_hard_delete(self, mock_db, sample_user):
        """Test hard delete of user"""
        # Act
        result = await UserService.delete_user(mock_db, sample_user, soft_delete=False)
        
        # Assert
        assert result is True
        mock_db.delete.assert_called_once_with(sample_user)
        mock_db.commit.assert_called_once()
    
    async def test_verify_email(self, mock_db, sample_user):
        """Test email verification"""
        # Arrange
        sample_user.is_verified = False
        sample_user.email_verification_token = "token123"
        
        # Act
        result = await UserService.verify_email(mock_db, sample_user)
        
        # Assert
        assert sample_user.is_verified is True
        assert sample_user.email_verification_token is None
        assert sample_user.email_verified_at is not None
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    async def test_get_user_statistics(self, mock_db, sample_user):
        """Test getting user statistics"""
        # Arrange
        mock_result1 = MagicMock()
        mock_result1.scalar.return_value = 5  # Total items
        
        mock_result2 = MagicMock()
        mock_result2.scalar.return_value = 3  # Active items
        
        mock_db.execute.side_effect = [mock_result1, mock_result2]
        
        # Act
        result = await UserService.get_user_statistics(mock_db, sample_user)
        
        # Assert
        assert result["total_items"] == 5
        assert result["active_items"] == 3
        assert result["email_verified"] is True
        assert "profile_completeness" in result
    
    def test_calculate_profile_completeness(self, sample_user):
        """Test profile completeness calculation"""
        # Act
        completeness = UserService._calculate_profile_completeness(sample_user)
        
        # Assert
        assert completeness == 80  # 4 out of 5 fields completed
    
    async def test_export_user_data(self, mock_db, sample_user):
        """Test user data export for GDPR compliance"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []  # No items
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await UserService.export_user_data(mock_db, sample_user, include_items=True)
        
        # Assert
        assert "user_info" in result
        assert result["user_info"]["email"] == sample_user.email
        assert "items" in result
        assert "export_date" in result
        assert result["total_items"] == 0