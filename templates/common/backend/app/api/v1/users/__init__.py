"""
Users API Module
Split into logical sub-modules for better organization
"""
from fastapi import APIRouter

from .profile import router as profile_router
from .management import router as management_router  
from .statistics import router as statistics_router
from .export import router as export_router

# Create main users router
router = APIRouter(prefix="/users", tags=["users"])

# Include sub-routers
router.include_router(profile_router, tags=["user-profile"])
router.include_router(management_router, tags=["user-management"])
router.include_router(statistics_router, tags=["user-statistics"])
router.include_router(export_router, tags=["user-export"])

__all__ = ["router"]