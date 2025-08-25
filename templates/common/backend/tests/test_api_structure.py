"""
Test API Structure and Response Formats
Ensures API endpoints maintain consistent response structures
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import User
from app.core.config import settings


class TestAPIResponseStructure:
    """Test that API responses maintain expected structure"""
    
    def test_user_endpoints_response_format(self, client: TestClient, test_superuser_headers: dict):
        """Verify user endpoint response formats"""
        
        # Test GET /users returns list of users
        response = client.get("/api/v1/users/", headers=test_superuser_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:  # If there are users
            user = data[0]
            assert "id" in user
            assert "email" in user
            assert "is_active" in user
    
    def test_user_update_returns_user_object(self, client: TestClient, test_user: User, test_superuser_headers: dict):
        """Test that user update endpoint returns user object directly"""
        update_data = {"full_name": "Updated Name"}
        
        response = client.put(
            f"/api/v1/users/{test_user.id}",
            json=update_data,
            headers=test_superuser_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return user object directly, not wrapped in response
        assert "id" in data
        assert "email" in data
        assert "full_name" in data
        assert data["full_name"] == "Updated Name"
        
        # Should NOT have wrapper fields
        assert "success" not in data
        assert "message" not in data
        assert "user" not in data
    
    def test_user_create_returns_response_wrapper(self, client: TestClient, test_superuser_headers: dict):
        """Test that user create endpoint returns wrapped response"""
        user_data = {
            "email": "newuser@example.com",
            "password": "StrongPass123!",
            "username": "newuser",
            "full_name": "New User",
            "is_active": True,
            "is_verified": False,
            "is_superuser": False
        }
        
        response = client.post(
            "/api/v1/users/",
            json=user_data,
            headers=test_superuser_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return wrapped response
        assert "message" in data
        assert "user" in data
        assert data["message"] == "User created successfully"
        assert data["user"]["email"] == "newuser@example.com"
    
    def test_user_delete_returns_message(self, client: TestClient, test_user: User, test_superuser_headers: dict):
        """Test that user delete endpoint returns message response"""
        response = client.delete(
            f"/api/v1/users/{test_user.id}",
            headers=test_superuser_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return message response
        assert "message" in data
        assert data["message"] == "User deleted successfully"
        
        # Should NOT have user data
        assert "user" not in data
        assert "id" not in data
    
    def test_profile_update_returns_wrapped_response(self, client: TestClient, test_headers: dict):
        """Test that profile update returns wrapped response"""
        update_data = {"full_name": "Updated Profile"}
        
        response = client.put(
            "/api/v1/users/me",
            json=update_data,
            headers=test_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Profile update should return wrapped response
        assert "message" in data
        assert "user" in data
        # Note: success field is in UserResponse
        assert "success" in data  
        assert data["user"]["full_name"] == "Updated Profile"
    
    def test_get_current_user_returns_user_object(self, client: TestClient, test_headers: dict):
        """Test that get current user returns user object directly"""
        response = client.get("/api/v1/users/me", headers=test_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return user object directly
        assert "id" in data
        assert "email" in data
        assert "is_active" in data
        
        # Should NOT have wrapper fields
        assert "success" not in data
        assert "message" not in data
        assert "user" not in data


class TestAPIModularStructure:
    """Test that modular API structure works correctly"""
    
    def test_users_module_imports(self):
        """Test that users module can be imported"""
        try:
            from app.api.v1.users import router
            from app.api.v1.users.profile import router as profile_router
            from app.api.v1.users.management import router as mgmt_router
            from app.api.v1.users.statistics import router as stats_router
            from app.api.v1.users.export import router as export_router
            assert router is not None
            assert profile_router is not None
            assert mgmt_router is not None
            assert stats_router is not None
            assert export_router is not None
        except ImportError as e:
            pytest.fail(f"Failed to import users module: {e}")
    
    def test_validators_module_imports(self):
        """Test that validators module can be imported"""
        try:
            from app.api.v1.validators import (
                validate_email,
                validate_username,
                validate_password_strength,
                validate_uuid
            )
            assert validate_email is not None
            assert validate_username is not None
            assert validate_password_strength is not None
            assert validate_uuid is not None
        except ImportError as e:
            pytest.fail(f"Failed to import validators module: {e}")
    
    def test_all_user_endpoints_accessible(self, client: TestClient, test_headers: dict):
        """Test that all user endpoints are accessible after modularization"""
        endpoints = [
            ("/api/v1/users/me", "get"),
            ("/api/v1/users/me/statistics", "get"),
            ("/api/v1/users/me/export", "get"),
        ]
        
        for endpoint, method in endpoints:
            if method == "get":
                response = client.get(endpoint, headers=test_headers)
                # We just check that endpoint exists (not 404)
                assert response.status_code != 404, f"Endpoint {endpoint} not found"


class TestValidatorFunctionality:
    """Test that validators work correctly"""
    
    def test_email_validation(self):
        """Test email validator"""
        from app.api.v1.validators import validate_email
        from fastapi import HTTPException
        
        # Valid email
        assert validate_email("user@example.com") == "user@example.com"
        
        # Invalid emails should raise HTTPException
        with pytest.raises(HTTPException):
            validate_email("invalid-email")
        
        with pytest.raises(HTTPException):
            validate_email("@example.com")
        
        with pytest.raises(HTTPException):
            validate_email("user@")
    
    def test_username_validation(self):
        """Test username validator"""
        from app.api.v1.validators import validate_username
        from fastapi import HTTPException
        
        # Valid usernames
        assert validate_username("validuser") == "validuser"
        assert validate_username("user_123") == "user_123"
        assert validate_username("user-name") == "user-name"
        
        # Invalid usernames should raise HTTPException
        with pytest.raises(HTTPException):
            validate_username("ab")  # Too short
        
        with pytest.raises(HTTPException):
            validate_username("user@name")  # Invalid character
        
        with pytest.raises(HTTPException):
            validate_username("admin")  # Reserved
    
    def test_password_strength_validation(self):
        """Test password strength validator"""
        from app.api.v1.validators import validate_password_strength
        
        # Strong password
        is_valid, errors = validate_password_strength("StrongPass123!")
        assert is_valid is True
        assert len(errors) == 0
        
        # Weak password
        is_valid, errors = validate_password_strength("weak")
        assert is_valid is False
        assert len(errors) > 0
        
        # Common password
        is_valid, errors = validate_password_strength("password123")
        assert is_valid is False
        assert any("common" in error.lower() for error in errors)