"""
Test configuration and fixtures for pytest
"""
import os
import sys
from typing import Generator, Any
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app
from app.db.database import Base, get_db, get_async_db
from tests.db_adapter import AsyncSessionAdapter

# Create a test app without lifespan for testing
from fastapi import FastAPI
from app.api.v1.api import api_router
from app.core.config import settings

test_app = FastAPI(
    title=settings.PROJECT_NAME + " - Test",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Add CORS middleware
from fastapi.middleware.cors import CORSMiddleware
test_app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
test_app.include_router(api_router, prefix=settings.API_V1_STR)
from app.models.user import User
from app.core.config import get_settings
from app.services.auth import AuthService

# Use PostgreSQL for tests - same as production but different database
# First try DATABASE_URL, then TEST_DATABASE_URL, then default
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    os.getenv(
        "TEST_DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/test_app_test"
    )
)

# For PostgreSQL, we don't need check_same_thread or StaticPool
if SQLALCHEMY_DATABASE_URL.startswith("postgresql"):
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
else:
    # Fallback to SQLite if needed
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    """Override database dependency for tests"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> TestClient:
    """Create a test client with database override"""
    async def override_get_async_db():
        yield AsyncSessionAdapter(db)
    
    test_app.dependency_overrides[get_db] = lambda: db
    test_app.dependency_overrides[get_async_db] = override_get_async_db
    with TestClient(test_app) as test_client:
        yield test_client
    test_app.dependency_overrides.clear()


@pytest.fixture
def test_user(db: Session) -> User:
    """Create a test user"""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=AuthService.get_password_hash("TestPass123!"),
        full_name="Test User",
        is_active=True,
        is_verified=False,
        is_superuser=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_superuser(db: Session) -> User:
    """Create a test superuser"""
    user = User(
        email="admin@example.com",
        username="admin",
        hashed_password=AuthService.get_password_hash("Admin123!"),
        full_name="Admin User",
        is_active=True,
        is_verified=True,
        is_superuser=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_token(test_user: User) -> str:
    """Create a test token for regular user"""
    return AuthService.create_access_token(data={"sub": str(test_user.id)})


@pytest.fixture
def test_superuser_token(test_superuser: User) -> str:
    """Create a test token for superuser"""
    return AuthService.create_access_token(data={"sub": str(test_superuser.id)})


@pytest.fixture
def test_headers(test_token: str) -> dict:
    """Create headers with auth token for regular user"""
    return {"Authorization": f"Bearer {test_token}"}


@pytest.fixture
def test_superuser_headers(test_superuser_token: str) -> dict:
    """Create headers with auth token for superuser"""
    return {"Authorization": f"Bearer {test_superuser_token}"}