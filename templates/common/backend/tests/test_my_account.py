"""
Tests for My Account functionality
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.models.user import User
from app.models.item import Item
from app.core.security import SecurityService
from tests.utils import create_test_user, get_auth_headers
import json


@pytest.mark.asyncio
async def test_get_user_stats(client: AsyncClient, db: AsyncSession):
    """Test getting user statistics"""
    # Create test user
    user = await create_test_user(db)
    headers = await get_auth_headers(client, user.email, "testpassword")
    
    # Create some items for the user
    for i in range(3):
        item = Item(
            title=f"Test Item {i}",
            description=f"Description {i}",
            price=100.0 * (i + 1),
            category="Electronics" if i < 2 else "Books",
            stock_quantity=10,
            owner_id=user.id
        )
        db.add(item)
    await db.commit()
    
    # Get stats
    response = await client.get("/api/v1/users/me/stats", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_items"] == 3
    assert data["total_value"] == 600.0  # 100 + 200 + 300
    assert data["average_item_price"] == 200.0
    assert "Electronics" in data["items_by_category"]
    assert data["items_by_category"]["Electronics"] == 2
    assert data["items_by_category"]["Books"] == 1
    assert data["account_age_days"] >= 0


@pytest.mark.asyncio
async def test_change_password(client: AsyncClient, db: AsyncSession):
    """Test password change functionality"""
    # Create test user
    user = await create_test_user(db)
    headers = await get_auth_headers(client, user.email, "testpassword")
    
    # Change password
    response = await client.post(
        "/api/v1/users/me/change-password",
        json={
            "current_password": "testpassword",
            "new_password": "newpassword123"
        },
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Password changed successfully"
    
    # Try to login with old password (should fail)
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": user.email,
            "password": "testpassword"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401
    
    # Login with new password (should succeed)
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": user.email,
            "password": "newpassword123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_change_password_wrong_current(client: AsyncClient, db: AsyncSession):
    """Test password change with wrong current password"""
    # Create test user
    user = await create_test_user(db)
    headers = await get_auth_headers(client, user.email, "testpassword")
    
    # Try to change password with wrong current password
    response = await client.post(
        "/api/v1/users/me/change-password",
        json={
            "current_password": "wrongpassword",
            "new_password": "newpassword123"
        },
        headers=headers
    )
    assert response.status_code == 400
    assert "Incorrect current password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_deactivate_account(client: AsyncClient, db: AsyncSession):
    """Test account deactivation"""
    # Create test user
    user = await create_test_user(db)
    headers = await get_auth_headers(client, user.email, "testpassword")
    
    # Deactivate account
    response = await client.post("/api/v1/users/me/deactivate", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Account deactivated successfully"
    
    # Try to login (should fail)
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": user.email,
            "password": "testpassword"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_export_user_data(client: AsyncClient, db: AsyncSession):
    """Test user data export"""
    # Create test user
    user = await create_test_user(db)
    headers = await get_auth_headers(client, user.email, "testpassword")
    
    # Create some items
    for i in range(2):
        item = Item(
            title=f"Export Test Item {i}",
            description=f"Description {i}",
            price=50.0 * (i + 1),
            category="Test",
            owner_id=user.id
        )
        db.add(item)
    await db.commit()
    
    # Export data
    response = await client.get("/api/v1/users/me/export", headers=headers)
    assert response.status_code == 200
    
    # Check response headers
    assert "application/json" in response.headers["content-type"]
    assert "attachment" in response.headers.get("content-disposition", "")
    
    # Check exported data
    data = response.json()
    assert "user" in data
    assert data["user"]["email"] == user.email
    assert "items" in data
    assert len(data["items"]) == 2
    assert data["items"][0]["title"] == "Export Test Item 0"
    assert "export_date" in data


@pytest.mark.asyncio
async def test_stats_no_items(client: AsyncClient, db: AsyncSession):
    """Test user stats when user has no items"""
    # Create test user
    user = await create_test_user(db)
    headers = await get_auth_headers(client, user.email, "testpassword")
    
    # Get stats (should return zeros)
    response = await client.get("/api/v1/users/me/stats", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_items"] == 0
    assert data["total_value"] == 0.0
    assert data["average_item_price"] == 0.0
    assert data["items_by_category"] == {}


@pytest.mark.asyncio
async def test_unauthenticated_access(client: AsyncClient):
    """Test that My Account endpoints require authentication"""
    endpoints = [
        ("/api/v1/users/me/stats", "GET"),
        ("/api/v1/users/me/change-password", "POST"),
        ("/api/v1/users/me/deactivate", "POST"),
        ("/api/v1/users/me/export", "GET")
    ]
    
    for endpoint, method in endpoints:
        if method == "GET":
            response = await client.get(endpoint)
        else:
            response = await client.post(endpoint, json={})
        
        assert response.status_code == 401, f"Endpoint {endpoint} should require auth"