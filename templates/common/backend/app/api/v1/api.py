from fastapi import APIRouter

from app.api.v1 import auth, users, admin
from app.api import health, items

api_router = APIRouter()

# Include all API v1 routes
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(admin.router)

# Include legacy routes (for backward compatibility)
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(items.router, prefix="/items", tags=["items"])