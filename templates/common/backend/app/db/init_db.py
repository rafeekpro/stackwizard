"""
Initialize database with first superuser
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.db.database import AsyncSessionLocal
from app.models.user import User
from app.services.auth import AuthService

async def init_db() -> None:
    """
    Initialize database with first superuser if it doesn't exist
    """
    async with AsyncSessionLocal() as db:
        # Check if any superuser exists
        result = await db.execute(
            select(User).where(User.is_superuser == True)
        )
        superuser = result.scalar_one_or_none()
        
        if not superuser:
            print("Creating first superuser...")
            
            # Create first superuser
            superuser = User(
                email=settings.FIRST_SUPERUSER_EMAIL,
                hashed_password=AuthService.get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                full_name="System Administrator",
                is_active=True,
                is_superuser=True,
                is_verified=True
            )
            
            db.add(superuser)
            await db.commit()
            await db.refresh(superuser)
            
            print(f"Superuser created with email: {settings.FIRST_SUPERUSER_EMAIL}")
        else:
            print("Superuser already exists")

if __name__ == "__main__":
    asyncio.run(init_db())