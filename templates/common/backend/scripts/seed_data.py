"""
Seed script to populate database with sample data
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.models.item import Item
from passlib.context import CryptContext

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
from app.core.config import settings
from uuid import uuid4
import json
import random

# Sample items data
SAMPLE_ITEMS = [
    {
        "title": "MacBook Pro 14",
        "description": "Apple MacBook Pro 14-inch with M3 Pro chip, 16GB RAM, 512GB SSD",
        "price": 1999.99,
        "category": "Electronics",
        "stock_quantity": 10,
        "image_url": "https://example.com/macbook.jpg",
        "rating": 4.8,
        "tags": json.dumps(["laptop", "apple", "computer", "professional"])
    },
    {
        "title": "iPhone 15 Pro",
        "description": "Latest iPhone with titanium design, A17 Pro chip, 256GB",
        "price": 1199.00,
        "category": "Electronics",
        "stock_quantity": 25,
        "image_url": "https://example.com/iphone.jpg",
        "rating": 4.7,
        "tags": json.dumps(["phone", "apple", "smartphone", "5g"])
    },
    {
        "title": "Sony WH-1000XM5",
        "description": "Premium noise-canceling wireless headphones",
        "price": 399.99,
        "category": "Audio",
        "stock_quantity": 15,
        "image_url": "https://example.com/sony-headphones.jpg",
        "rating": 4.6,
        "tags": json.dumps(["headphones", "wireless", "noise-canceling", "sony"])
    },
    {
        "title": "Samsung 65\" OLED TV",
        "description": "4K Smart TV with Quantum Dot technology",
        "price": 2499.99,
        "category": "Electronics",
        "stock_quantity": 5,
        "image_url": "https://example.com/samsung-tv.jpg",
        "rating": 4.5,
        "tags": json.dumps(["tv", "4k", "oled", "smart-tv"])
    },
    {
        "title": "Nike Air Max 2024",
        "description": "Latest Air Max sneakers with enhanced cushioning",
        "price": 159.99,
        "category": "Fashion",
        "stock_quantity": 30,
        "image_url": "https://example.com/nike-shoes.jpg",
        "rating": 4.4,
        "tags": json.dumps(["shoes", "nike", "sneakers", "sports"])
    },
    {
        "title": "Kindle Paperwhite",
        "description": "E-reader with 6.8\" display and adjustable warm light",
        "price": 149.99,
        "category": "Books",
        "stock_quantity": 20,
        "image_url": "https://example.com/kindle.jpg",
        "rating": 4.5,
        "tags": json.dumps(["ereader", "kindle", "books", "amazon"])
    },
    {
        "title": "PlayStation 5",
        "description": "Gaming console with 4K gaming and ultra-high-speed SSD",
        "price": 499.99,
        "category": "Gaming",
        "stock_quantity": 8,
        "image_url": "https://example.com/ps5.jpg",
        "rating": 4.8,
        "tags": json.dumps(["gaming", "console", "playstation", "sony"])
    },
    {
        "title": "Dyson V15 Vacuum",
        "description": "Cordless vacuum cleaner with laser dust detection",
        "price": 699.99,
        "category": "Home",
        "stock_quantity": 12,
        "image_url": "https://example.com/dyson.jpg",
        "rating": 4.6,
        "tags": json.dumps(["vacuum", "dyson", "cordless", "home"])
    },
    {
        "title": "iPad Pro 12.9",
        "description": "iPad Pro with M2 chip, 128GB, Wi-Fi + Cellular",
        "price": 1299.00,
        "category": "Electronics",
        "stock_quantity": 18,
        "image_url": "https://example.com/ipad.jpg",
        "rating": 4.7,
        "tags": json.dumps(["tablet", "apple", "ipad", "professional"])
    },
    {
        "title": "Canon EOS R6",
        "description": "Full-frame mirrorless camera with 20MP sensor",
        "price": 2499.00,
        "category": "Photography",
        "stock_quantity": 6,
        "image_url": "https://example.com/canon-camera.jpg",
        "rating": 4.8,
        "tags": json.dumps(["camera", "canon", "mirrorless", "photography"])
    },
    {
        "title": "Herman Miller Aeron Chair",
        "description": "Ergonomic office chair with lumbar support",
        "price": 1395.00,
        "category": "Furniture",
        "stock_quantity": 4,
        "image_url": "https://example.com/aeron-chair.jpg",
        "rating": 4.9,
        "tags": json.dumps(["chair", "office", "ergonomic", "herman-miller"])
    },
    {
        "title": "Apple Watch Series 9",
        "description": "Smartwatch with health tracking and fitness features",
        "price": 429.00,
        "category": "Wearables",
        "stock_quantity": 22,
        "image_url": "https://example.com/apple-watch.jpg",
        "rating": 4.6,
        "tags": json.dumps(["smartwatch", "apple", "fitness", "health"])
    }
]

async def seed_database():
    """Seed the database with sample data"""
    
    # Create async engine
    engine = create_async_engine(
        settings.ASYNC_DATABASE_URL,
        echo=True
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Check if data already exists
        result = await session.execute(select(User).limit(1))
        if result.scalar():
            print("Database already has data. Skipping seed.")
            return
        
        # Create sample users
        users = []
        
        # Admin user
        admin_user = User(
            id=uuid4(),
            email="admin@example.com",
            username="admin",
            full_name="Admin User",
            hashed_password=pwd_context.hash("admin123"),
            is_active=True,
            is_superuser=True,
            is_verified=True
        )
        users.append(admin_user)
        session.add(admin_user)
        
        # Regular users
        for i in range(1, 4):
            user = User(
                id=uuid4(),
                email=f"user{i}@example.com",
                username=f"user{i}",
                full_name=f"Test User {i}",
                hashed_password=pwd_context.hash(f"password{i}"),
                is_active=True,
                is_superuser=False,
                is_verified=True
            )
            users.append(user)
            session.add(user)
        
        await session.flush()
        
        # Create sample items
        for item_data in SAMPLE_ITEMS:
            # Randomly assign to a user
            owner = random.choice(users)
            
            item = Item(
                **item_data,
                owner_id=owner.id,
                is_available=True
            )
            session.add(item)
        
        # Create some additional random items for variety
        categories = ["Electronics", "Books", "Fashion", "Home", "Sports", "Food", "Toys"]
        for i in range(20):
            item = Item(
                title=f"Sample Product {i+1}",
                description=f"This is a sample product description for item {i+1}",
                price=round(random.uniform(10, 500), 2),
                category=random.choice(categories),
                stock_quantity=random.randint(1, 50),
                rating=round(random.uniform(3.0, 5.0), 1),
                tags=json.dumps([f"tag{i}", "sample"]),
                is_available=random.choice([True, True, True, False]),  # 75% available
                owner_id=random.choice(users).id
            )
            session.add(item)
        
        await session.commit()
        print("✅ Database seeded successfully!")
        print(f"Created {len(users)} users and {len(SAMPLE_ITEMS) + 20} items")
        print("\nSample credentials:")
        print("  Admin: admin@example.com / admin123")
        print("  User1: user1@example.com / password1")
        print("  User2: user2@example.com / password2")
        print("  User3: user3@example.com / password3")
    
    await engine.dispose()

if __name__ == "__main__":
    import sys
    from sqlalchemy import select
    
    # Add parent directory to path
    sys.path.append('..')
    
    asyncio.run(seed_database())