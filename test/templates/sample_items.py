async def create_sample_items(db: AsyncSession, user: User) -> None:
    """Create sample items for testing"""
    from app.models.item import Item
    
    # Check if items exist
    result = await db.execute(select(Item).limit(1))
    existing_items = result.scalar_one_or_none()
    
    if not existing_items:
        print("Creating sample items...")
        sample_items = [
            Item(
                title="Sample Laptop",
                description="High-performance laptop for development",
                owner_id=user.id
            ),
            Item(
                title="Wireless Mouse",
                description="Ergonomic wireless mouse with long battery life",
                owner_id=user.id
            ),
            Item(
                title="Mechanical Keyboard",
                description="RGB mechanical keyboard with cherry switches",
                owner_id=user.id
            ),
        ]
        
        for item in sample_items:
            db.add(item)
        
        await db.commit()
        print(f"Created {len(sample_items)} sample items")