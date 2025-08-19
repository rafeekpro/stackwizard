"""
Test user management endpoints
Following TDD methodology
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.auth import AuthService


class TestUserEndpoints:
    """Test user management API endpoints"""
    
    def test_get_current_user(self, client: TestClient, test_user: User, test_headers: dict):
        """Test getting current user info"""
        response = client.get("/api/v1/users/me", headers=test_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_user.id)
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
        assert data["full_name"] == test_user.full_name
        assert data["is_active"] == test_user.is_active
        assert data["is_superuser"] == test_user.is_superuser
        assert data["is_verified"] == test_user.is_verified
        assert "hashed_password" not in data
    
    def test_get_current_user_unauthorized(self, client: TestClient):
        """Test getting current user without auth"""
        response = client.get("/api/v1/users/me")
        
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
    
    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test getting current user with invalid token"""
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.get("/api/v1/users/me", headers=headers)
        
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]
    
    def test_update_current_user(self, client: TestClient, test_user: User, test_headers: dict):
        """Test updating current user info"""
        update_data = {
            "full_name": "Updated Name",
            "username": "updatedusername"
        }
        
        response = client.put(
            "/api/v1/users/me",
            json=update_data,
            headers=test_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["username"] == "updatedusername"
        assert data["email"] == test_user.email  # Email unchanged
    
    def test_update_current_user_duplicate_email(
        self, client: TestClient, test_user: User, test_superuser: User, test_headers: dict
    ):
        """Test updating user with duplicate email"""
        update_data = {
            "email": test_superuser.email  # Try to use existing email
        }
        
        response = client.put(
            "/api/v1/users/me",
            json=update_data,
            headers=test_headers
        )
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()
    
    def test_update_user_password(self, client: TestClient, test_user: User, test_headers: dict):
        """Test changing user password"""
        password_data = {
            "current_password": "TestPass123!",
            "new_password": "NewTestPass123!"
        }
        
        response = client.put(
            "/api/v1/users/me/password",
            json=password_data,
            headers=test_headers
        )
        
        assert response.status_code == 200
        assert "Password updated successfully" in response.json()["message"]
        
        # Try login with new password
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "NewTestPass123!"
            }
        )
        assert login_response.status_code == 200
    
    def test_update_password_wrong_current(self, client: TestClient, test_user: User, test_headers: dict):
        """Test changing password with wrong current password"""
        password_data = {
            "current_password": "WrongPassword",
            "new_password": "NewTestPass123!"
        }
        
        response = client.put(
            "/api/v1/users/me/password",
            json=password_data,
            headers=test_headers
        )
        
        assert response.status_code == 400
        assert "Incorrect password" in response.json()["detail"]
    
    def test_delete_current_user(self, client: TestClient, test_user: User, test_headers: dict):
        """Test soft-deleting current user"""
        response = client.delete("/api/v1/users/me", headers=test_headers)
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"].lower()
        
        # User should be soft-deleted (is_active = False)
        # Try to login again
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "TestPass123!"
            }
        )
        assert login_response.status_code == 401  # Should fail


class TestAdminUserEndpoints:
    """Test admin-only user management endpoints"""
    
    def test_get_all_users_as_admin(self, client: TestClient, test_superuser: User, test_superuser_headers: dict):
        """Test getting all users as admin"""
        response = client.get("/api/v1/users/", headers=test_superuser_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # At least the admin user
        
        # Check user data structure
        for user in data:
            assert "id" in user
            assert "email" in user
            assert "username" in user
            assert "is_active" in user
            assert "hashed_password" not in user
    
    def test_get_all_users_as_regular_user(self, client: TestClient, test_user: User, test_headers: dict):
        """Test that regular users cannot get all users"""
        response = client.get("/api/v1/users/", headers=test_headers)
        
        assert response.status_code == 403
        assert "Not enough permissions" in response.json()["detail"]
    
    def test_get_all_users_with_pagination(self, client: TestClient, test_superuser_headers: dict, db: Session):
        """Test pagination in user list"""
        # Create multiple users
        for i in range(5):
            user = User(
                email=f"user{i}@example.com",
                username=f"user{i}",
                hashed_password=AuthService.get_password_hash("Pass123!")
            )
            db.add(user)
        db.commit()
        
        # Get first page
        response = client.get("/api/v1/users/?skip=0&limit=2", headers=test_superuser_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # Get second page
        response = client.get("/api/v1/users/?skip=2&limit=2", headers=test_superuser_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_get_user_by_id_as_admin(
        self, client: TestClient, test_user: User, test_superuser_headers: dict
    ):
        """Test getting specific user by ID as admin"""
        response = client.get(f"/api/v1/users/{test_user.id}", headers=test_superuser_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_user.id)
        assert data["email"] == test_user.email
    
    def test_get_user_by_id_not_found(self, client: TestClient, test_superuser_headers: dict):
        """Test getting non-existent user"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/v1/users/{fake_id}", headers=test_superuser_headers)
        
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
    
    def test_update_user_by_admin(
        self, client: TestClient, test_user: User, test_superuser_headers: dict
    ):
        """Test admin updating another user"""
        update_data = {
            "full_name": "Admin Updated Name",
            "is_verified": True,
            "is_active": False
        }
        
        response = client.put(
            f"/api/v1/users/{test_user.id}",
            json=update_data,
            headers=test_superuser_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Admin Updated Name"
        assert data["is_verified"] is True
        assert data["is_active"] is False
    
    def test_update_user_make_superuser(
        self, client: TestClient, test_user: User, test_superuser_headers: dict
    ):
        """Test admin making another user a superuser"""
        update_data = {"is_superuser": True}
        
        response = client.put(
            f"/api/v1/users/{test_user.id}",
            json=update_data,
            headers=test_superuser_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_superuser"] is True
    
    def test_delete_user_by_admin(
        self, client: TestClient, test_user: User, test_superuser_headers: dict, db: Session
    ):
        """Test admin deleting another user"""
        response = client.delete(
            f"/api/v1/users/{test_user.id}",
            headers=test_superuser_headers
        )
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"].lower()
        
        # Check user is soft-deleted
        db.refresh(test_user)
        assert test_user.is_active is False
    
    def test_create_user_by_admin(self, client: TestClient, test_superuser_headers: dict):
        """Test admin creating a new user"""
        new_user_data = {
            "email": "adminCreated@example.com",
            "password": "AdminCreated123!",
            "username": "admincreated",
            "full_name": "Admin Created User",
            "is_verified": True,
            "is_superuser": False
        }
        
        response = client.post(
            "/api/v1/users/",
            json=new_user_data,
            headers=test_superuser_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "adminCreated@example.com"
        assert data["username"] == "admincreated"
        assert data["is_verified"] is True
        assert data["is_superuser"] is False


class TestPasswordRecovery:
    """Test password recovery functionality"""
    
    def test_request_password_reset(self, client: TestClient, test_user: User):
        """Test requesting password reset"""
        response = client.post(
            "/api/v1/auth/password-recovery",
            json={"email": test_user.email}
        )
        
        assert response.status_code == 200
        assert "Password recovery email sent" in response.json()["message"]
    
    def test_request_password_reset_nonexistent_email(self, client: TestClient):
        """Test password reset for non-existent email"""
        response = client.post(
            "/api/v1/auth/password-recovery",
            json={"email": "nonexistent@example.com"}
        )
        
        # Should return success to not leak information
        assert response.status_code == 200
        assert "Password recovery email sent" in response.json()["message"]
    
    def test_reset_password_with_token(self, client: TestClient, test_user: User):
        """Test resetting password with valid token"""
        # In real implementation, this would be a token from email
        # For testing, we'll create a valid token
        reset_token = AuthService.create_password_reset_token()
        
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "email": test_user.email,
                "token": reset_token,
                "new_password": "ResetPass123!"
            }
        )
        
        assert response.status_code == 200
        assert "Password reset successfully" in response.json()["message"]
        
        # Try login with new password
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "ResetPass123!"
            }
        )
        assert login_response.status_code == 200
    
    def test_reset_password_invalid_token(self, client: TestClient, test_user: User):
        """Test resetting password with invalid token"""
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "email": test_user.email,
                "token": "invalid-token",
                "new_password": "ResetPass123!"
            }
        )
        
        assert response.status_code == 400
        assert "Invalid or expired reset token" in response.json()["detail"]