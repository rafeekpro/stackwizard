"""
Initialize database with first superuser
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.db.database import AsyncSessionLocal
from app.models.user import User
from app.models.item import Item
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
                username=settings.FIRST_SUPERUSER_USERNAME,
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
            
            # Create sample items for the superuser
            await create_sample_items(db, superuser)
        else:
            print("Superuser already exists")
            
            # Ensure sample items exist
            await create_sample_items(db, superuser)

async def create_sample_items(db: AsyncSession, user: User) -> None:
    """Create sample items for demonstration"""
    # Check if items already exist
    result = await db.execute(select(Item).limit(1))
    existing_items = result.scalar_one_or_none()
    
    if not existing_items:
        print("Creating sample items...")
        sample_items = [
            Item(
                title="Sample Laptop",
                description="High-performance laptop for development work",
                owner_id=user.id
            ),
            Item(
                title="Wireless Mouse",
                description="Ergonomic wireless mouse with long battery life",
                owner_id=user.id
            ),
            Item(
                title="Mechanical Keyboard",
                description="RGB mechanical keyboard with cherry MX switches",
                owner_id=user.id
            ),
            Item(
                title="4K Monitor",
                description="Ultra HD monitor for professional work",
                owner_id=user.id
            ),
            Item(
                title="USB-C Hub",
                description="Multi-port USB-C hub with HDMI and ethernet",
                owner_id=user.id
            ),
        ]
        
        for item in sample_items:
            db.add(item)
        
        await db.commit()
        print(f"Created {len(sample_items)} sample items")
    else:
        print("Sample items already exist")

if __name__ == "__main__":
    asyncio.run(init_db())