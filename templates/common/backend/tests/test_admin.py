"""
Test admin-only endpoints
Following TDD methodology
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.auth import AuthService


class TestAdminDashboard:
    """Test admin dashboard endpoints"""
    
    def test_get_system_stats_as_admin(self, client: TestClient, test_superuser_headers: dict, db: Session):
        """Test getting system statistics as admin"""
        # Create some test data
        for i in range(3):
            user = User(
                email=f"stat{i}@example.com",
                username=f"statuser{i}",
                hashed_password=AuthService.get_password_hash("Pass123!"),
                is_active=i != 2,  # Last user is inactive
                is_verified=i == 0  # Only first is verified
            )
            db.add(user)
        db.commit()
        
        response = client.get("/api/v1/admin/stats", headers=test_superuser_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "active_users" in data
        assert "verified_users" in data
        assert "superusers" in data
        assert data["total_users"] >= 4  # 3 created + 1 admin
        assert data["active_users"] >= 3  # 2 active created + 1 admin
        assert data["verified_users"] >= 2  # 1 verified created + 1 admin
        assert data["superusers"] >= 1  # At least the admin
    
    def test_get_system_stats_as_regular_user(self, client: TestClient, test_headers: dict):
        """Test that regular users cannot access system stats"""
        response = client.get("/api/v1/admin/stats", headers=test_headers)
        
        assert response.status_code == 403
        assert "Not enough permissions" in response.json()["detail"]
    
    def test_get_recent_registrations(self, client: TestClient, test_superuser_headers: dict, db: Session):
        """Test getting recent user registrations"""
        response = client.get("/api/v1/admin/recent-registrations", headers=test_superuser_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should be sorted by created_at desc
        if len(data) > 1:
            first_date = data[0]["created_at"]
            second_date = data[1]["created_at"]
            assert first_date >= second_date
    
    def test_search_users_by_email(self, client: TestClient, test_superuser_headers: dict, db: Session):
        """Test searching users by email"""
        # Create test users
        user = User(
            email="searchme@example.com",
            username="searchuser",
            hashed_password=get_password_hash("Pass123!")
        )
        db.add(user)
        db.commit()
        
        response = client.get(
            "/api/v1/admin/users/search?email=searchme",
            headers=test_superuser_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(u["email"] == "searchme@example.com" for u in data)
    
    def test_bulk_activate_users(self, client: TestClient, test_superuser_headers: dict, db: Session):
        """Test bulk activating users"""
        # Create inactive users
        user_ids = []
        for i in range(3):
            user = User(
                email=f"inactive{i}@example.com",
                username=f"inactive{i}",
                hashed_password=AuthService.get_password_hash("Pass123!"),
                is_active=False
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            user_ids.append(str(user.id))
        
        response = client.post(
            "/api/v1/admin/users/bulk-activate",
            json={"user_ids": user_ids},
            headers=test_superuser_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["activated"] == 3
        
        # Verify users are active
        for user_id in user_ids:
            user = db.query(User).filter(User.id == user_id).first()
            assert user.is_active is True
    
    def test_bulk_deactivate_users(self, client: TestClient, test_superuser_headers: dict, db: Session):
        """Test bulk deactivating users"""
        # Create active users
        user_ids = []
        for i in range(2):
            user = User(
                email=f"active{i}@example.com",
                username=f"active{i}",
                hashed_password=AuthService.get_password_hash("Pass123!"),
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            user_ids.append(str(user.id))
        
        response = client.post(
            "/api/v1/admin/users/bulk-deactivate",
            json={"user_ids": user_ids},
            headers=test_superuser_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["deactivated"] == 2
        
        # Verify users are inactive
        for user_id in user_ids:
            user = db.query(User).filter(User.id == user_id).first()
            assert user.is_active is False


class TestAdminAuditLog:
    """Test admin audit log functionality"""
    
    def test_log_admin_action(self, client: TestClient, test_superuser: User, test_superuser_headers: dict):
        """Test that admin actions are logged"""
        # Perform an admin action
        response = client.get("/api/v1/users/", headers=test_superuser_headers)
        assert response.status_code == 200
        
        # Check audit log
        log_response = client.get("/api/v1/admin/audit-log", headers=test_superuser_headers)
        
        assert log_response.status_code == 200
        data = log_response.json()
        assert isinstance(data, list)
        # Should contain the recent action
        if len(data) > 0:
            assert "admin_id" in data[0]
            assert "action" in data[0]
            assert "timestamp" in data[0]
            assert data[0]["admin_id"] == str(test_superuser.id)
    
    def test_audit_log_access_denied_for_regular_user(self, client: TestClient, test_headers: dict):
        """Test that regular users cannot access audit log"""
        response = client.get("/api/v1/admin/audit-log", headers=test_headers)
        
        assert response.status_code == 403
        assert "Not enough permissions" in response.json()["detail"]


class TestAdminUserManagement:
    """Test advanced admin user management"""
    
    def test_admin_reset_user_password(
        self, client: TestClient, test_user: User, test_superuser_headers: dict
    ):
        """Test admin resetting another user's password"""
        response = client.post(
            f"/api/v1/admin/users/{test_user.id}/reset-password",
            json={"new_password": "AdminReset123!"},
            headers=test_superuser_headers
        )
        
        assert response.status_code == 200
        assert "Password reset successfully" in response.json()["message"]
        
        # User should be able to login with new password
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "AdminReset123!"
            }
        )
        assert login_response.status_code == 200
    
    def test_admin_verify_user_email(
        self, client: TestClient, test_user: User, test_superuser_headers: dict, db: Session
    ):
        """Test admin manually verifying user email"""
        # Ensure user is not verified
        test_user.is_verified = False
        db.commit()
        
        response = client.post(
            f"/api/v1/admin/users/{test_user.id}/verify-email",
            headers=test_superuser_headers
        )
        
        assert response.status_code == 200
        assert "Email verified successfully" in response.json()["message"]
        
        # Check user is verified
        db.refresh(test_user)
        assert test_user.is_verified is True
    
    def test_admin_export_users(self, client: TestClient, test_superuser_headers: dict):
        """Test exporting user data"""
        response = client.get(
            "/api/v1/admin/users/export?format=csv",
            headers=test_superuser_headers
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment" in response.headers["content-disposition"]
        
        # Check CSV content
        content = response.text
        assert "email" in content
        assert "username" in content
        assert "is_active" in content
    
    def test_admin_import_users(self, client: TestClient, test_superuser_headers: dict):
        """Test bulk importing users"""
        import_data = {
            "users": [
                {
                    "email": "import1@example.com",
                    "username": "import1",
                    "password": "Import123!",
                    "full_name": "Imported User 1"
                },
                {
                    "email": "import2@example.com",
                    "username": "import2",
                    "password": "Import123!",
                    "full_name": "Imported User 2"
                }
            ]
        }
        
        response = client.post(
            "/api/v1/admin/users/import",
            json=import_data,
            headers=test_superuser_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["imported"] == 2
        assert data["failed"] == 0
    
    def test_admin_get_user_sessions(
        self, client: TestClient, test_user: User, test_superuser_headers: dict
    ):
        """Test getting active sessions for a user"""
        response = client.get(
            f"/api/v1/admin/users/{test_user.id}/sessions",
            headers=test_superuser_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Each session should have required fields
        for session in data:
            assert "session_id" in session
            assert "created_at" in session
            assert "last_accessed" in session
            assert "ip_address" in session
    
    def test_admin_revoke_user_sessions(
        self, client: TestClient, test_user: User, test_superuser_headers: dict
    ):
        """Test revoking all sessions for a user"""
        response = client.post(
            f"/api/v1/admin/users/{test_user.id}/revoke-sessions",
            headers=test_superuser_headers
        )
        
        assert response.status_code == 200
        assert "All sessions revoked" in response.json()["message"]