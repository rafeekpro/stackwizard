from fastapi import APIRouter

from app.api.v1 import auth, admin, items
from app.api.v1.users import router as users_router
from app.api import health

api_router = APIRouter()

# Include all API v1 routes
api_router.include_router(auth.router)
api_router.include_router(users_router)
api_router.include_router(admin.router)
api_router.include_router(items.router)

# Include legacy routes (for backward compatibility)
api_router.include_router(health.router, prefix="/health", tags=["health"])