from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.init_db import init_db
from app.db.database import get_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting StackWizard Backend...")
    await init_db()  # Initialize database with superuser
    print("✅ Database initialized")
    yield
    # Shutdown
    print("👋 Shutting down StackWizard Backend...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="🧙‍♂️ StackWizard Backend API with Authentication",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "message": "🧙‍♂️ Welcome to StackWizard Backend",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health",
        "auth": {
            "login": f"{settings.API_V1_STR}/auth/login",
            "register": f"{settings.API_V1_STR}/auth/register",
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "stackwizard-backend",
        "version": settings.VERSION
    }

@app.get("/health/db")
def database_health_check(db: Session = Depends(get_db)):
    """Database health check endpoint"""
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

@app.get("/api/health")
def api_health_check():
    """Health check endpoint for frontend"""
    return {
        "status": "healthy",
        "service": "stackwizard-backend",
        "version": settings.VERSION
    }

@app.get("/api/health/db")
def api_database_health_check(db: Session = Depends(get_db)):
    """Database health check endpoint for frontend"""
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


@app.get("/favicon.ico")
async def favicon():
    """Return empty favicon to prevent 404 errors"""
    from fastapi.responses import Response
    return Response(content="", media_type="image/x-icon")