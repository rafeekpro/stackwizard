"""
Test authentication functionality
Following TDD - write tests first
"""
import pytest
from datetime import datetime, timedelta
from jose import jwt
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.auth import AuthService
from app.models.user import User
from app.core.config import get_settings

settings = get_settings()


class TestPasswordHashing:
    """Test password hashing and verification"""
    
    def test_password_hash_is_different_from_plain(self):
        """Test that hashed password is different from plain text"""
        plain_password = "TestPassword123!"
        hashed = AuthService.get_password_hash(plain_password)
        
        assert hashed != plain_password
        assert len(hashed) > 50  # Bcrypt hashes are long
        assert hashed.startswith("$2b$")  # Bcrypt prefix
    
    def test_same_password_different_hashes(self):
        """Test that same password generates different hashes (salt)"""
        plain_password = "TestPassword123!"
        hash1 = AuthService.get_password_hash(plain_password)
        hash2 = AuthService.get_password_hash(plain_password)
        
        assert hash1 != hash2  # Different salts
    
    def test_verify_correct_password(self):
        """Test verifying correct password"""
        plain_password = "TestPassword123!"
        hashed = AuthService.get_password_hash(plain_password)
        
        assert AuthService.verify_password(plain_password, hashed) is True
    
    def test_verify_incorrect_password(self):
        """Test verifying incorrect password"""
        plain_password = "TestPassword123!"
        hashed = AuthService.get_password_hash(plain_password)
        
        assert AuthService.verify_password("WrongPassword", hashed) is False


class TestJWTTokens:
    """Test JWT token creation and verification"""
    
    def test_create_access_token(self):
        """Test access token creation"""
        user_id = "test-user-id"
        token = AuthService.create_access_token(data={"sub": user_id})
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 50
        
        # Decode and verify
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        assert payload["sub"] == user_id
        assert "exp" in payload
    
    def test_create_refresh_token(self):
        """Test refresh token creation"""
        user_id = "test-user-id"
        token = AuthService.create_refresh_token(data={"sub": user_id})
        
        assert token is not None
        assert isinstance(token, str)
        
        # Decode and verify
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"
        assert "exp" in payload
    
    def test_access_token_expiration(self):
        """Test that access token has correct expiration"""
        user_id = "test-user-id"
        token = AuthService.create_access_token(data={"sub": user_id})
        
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        exp_time = datetime.fromtimestamp(payload["exp"])
        now = datetime.utcnow()
        
        # Should expire in about 30 minutes (default)
        time_diff = exp_time - now
        assert time_diff.total_seconds() > 1700  # More than 28 minutes
        assert time_diff.total_seconds() < 1900  # Less than 32 minutes
    
    def test_refresh_token_longer_expiration(self):
        """Test that refresh token has longer expiration than access token"""
        user_id = "test-user-id"
        refresh_token = create_refresh_token(subject=user_id)
        
        payload = jwt.decode(
            refresh_token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        exp_time = datetime.fromtimestamp(payload["exp"])
        now = datetime.utcnow()
        
        # Should expire in about 7 days (default)
        time_diff = exp_time - now
        assert time_diff.days >= 6  # At least 6 days
        assert time_diff.days <= 8  # At most 8 days
    
    def test_verify_valid_token(self):
        """Test verifying a valid token"""
        user_id = "test-user-id"
        token = AuthService.create_access_token(data={"sub": user_id})
        
        token_data = AuthService.verify_token(token)
        verified_user_id = str(token_data.user_id) if token_data else None
        assert verified_user_id == user_id
    
    def test_verify_invalid_token(self):
        """Test verifying an invalid token"""
        invalid_token = "invalid.token.here"
        
        token_data = AuthService.verify_token(invalid_token)
        verified_user_id = str(token_data.user_id) if token_data else None
        assert verified_user_id is None
    
    def test_verify_expired_token(self):
        """Test verifying an expired token"""
        user_id = "test-user-id"
        # Create token that expires immediately
        token = AuthService.create_access_token(
            data={"sub": user_id}, 
            expires_delta=timedelta(seconds=-1)
        )
        
        token_data = AuthService.verify_token(token)
        verified_user_id = str(token_data.user_id) if token_data else None
        assert verified_user_id is None


class TestAuthentication:
    """Test user authentication"""
    
    async def test_authenticate_valid_user(self, db: Session):
        """Test authenticating a valid user"""
        # Create user
        user = User(
            email="auth@example.com",
            username="authuser",
            hashed_password=AuthService.get_password_hash("ValidPass123!")
        )
        db.add(user)
        db.commit()
        
        # Authenticate
        authenticated = await AuthService.authenticate_user(db, "auth@example.com", "ValidPass123!")
        assert authenticated is not None
        assert authenticated.email == "auth@example.com"
    
    async def test_authenticate_invalid_password(self, db: Session):
        """Test authentication with wrong password"""
        # Create user
        user = User(
            email="wrong@example.com",
            username="wronguser",
            hashed_password=AuthService.get_password_hash("ValidPass123!")
        )
        db.add(user)
        db.commit()
        
        # Try to authenticate with wrong password
        authenticated = await AuthService.authenticate_user(db, "wrong@example.com", "WrongPassword")
        assert authenticated is False
    
    async def test_authenticate_nonexistent_user(self, db: Session):
        """Test authentication with non-existent user"""
        authenticated = await AuthService.authenticate_user(db, "nonexistent@example.com", "SomePass123!")
        assert authenticated is False
    
    async def test_authenticate_inactive_user(self, db: Session):
        """Test that inactive users cannot authenticate"""
        # Create inactive user
        user = User(
            email="inactive@example.com",
            username="inactiveuser",
            hashed_password=AuthService.get_password_hash("ValidPass123!"),
            is_active=False
        )
        db.add(user)
        db.commit()
        
        # Try to authenticate
        authenticated = await AuthService.authenticate_user(db, "inactive@example.com", "ValidPass123!")
        assert authenticated is False
    
    async def test_authenticate_updates_login_tracking(self, db: Session):
        """Test that successful authentication updates login tracking"""
        # Create user
        user = User(
            email="tracking@example.com",
            username="trackinguser",
            hashed_password=AuthService.get_password_hash("ValidPass123!"),
            login_count=0
        )
        db.add(user)
        db.commit()
        
        original_count = user.login_count
        original_login_time = user.last_login_at
        
        # Authenticate
        authenticated = await AuthService.authenticate_user(db, "tracking@example.com", "ValidPass123!")
        assert authenticated is not None
        
        # Check login tracking was updated
        db.refresh(user)
        assert user.login_count == original_count + 1
        assert user.last_login_at is not None
        if original_login_time:
            assert user.last_login_at > original_login_time


class TestAuthEndpoints:
    """Test authentication API endpoints"""
    
    def test_login_endpoint_success(self, client: TestClient, test_user: User):
        """Test successful login"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "TestPass123!"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
    
    def test_login_endpoint_invalid_password(self, client: TestClient, test_user: User):
        """Test login with invalid password"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "WrongPassword"
            }
        )
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    def test_login_endpoint_nonexistent_user(self, client: TestClient):
        """Test login with non-existent user"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "SomePassword123!"
            }
        )
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    def test_register_endpoint_success(self, client: TestClient):
        """Test successful registration"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "NewPass123!",
                "username": "newuser",
                "full_name": "New User"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["username"] == "newuser"
        assert data["user"]["full_name"] == "New User"
        assert "hashed_password" not in data["user"]  # Should not expose
    
    def test_register_endpoint_duplicate_email(self, client: TestClient, test_user: User):
        """Test registration with duplicate email"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,  # Duplicate
                "password": "AnotherPass123!",
                "username": "anotheruser"
            }
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_register_endpoint_weak_password(self, client: TestClient):
        """Test registration with weak password"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "weak@example.com",
                "password": "weak",  # Too short
                "username": "weakuser"
            }
        )
        
        assert response.status_code == 422
        assert "validation error" in response.json()["detail"].lower()
    
    def test_refresh_token_endpoint(self, client: TestClient, test_user: User):
        """Test refresh token endpoint"""
        # First login to get tokens
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "TestPass123!"
            }
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # Use refresh token
        response = client.post(
            f"/api/v1/auth/refresh?refresh_token={refresh_token}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_refresh_token_invalid(self, client: TestClient):
        """Test refresh with invalid token"""
        response = client.post(
            "/api/v1/auth/refresh?refresh_token=invalid-token"
        )
        
        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["detail"]