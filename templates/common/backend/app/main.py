from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.init_db import init_db

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


@app.get("/favicon.ico")
async def favicon():
    """Return empty favicon to prevent 404 errors"""
    from fastapi.responses import Response
    return Response(content="", media_type="image/x-icon")