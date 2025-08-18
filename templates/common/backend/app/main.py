from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, users, items
from app.core.config import settings
from app.db.database import engine
from app.models import base

base.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Full-stack application backend API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(items.router, prefix="/api/items", tags=["items"])

@app.get("/")
def root():
    return {
        "message": "Welcome to FastAPI Backend",
        "docs": "/docs",
        "health": "/api/health"
    }