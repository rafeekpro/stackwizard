# 🗄️ Database Schema

This page documents the PostgreSQL database structure, relationships, and design patterns used in StackWizard-generated projects.

## 📊 Entity Relationship Diagram

```mermaid
erDiagram
    USERS ||--o{ ITEMS : owns
    
    USERS {
        uuid id PK
        string email UK
        string username UK
        string hashed_password
        string full_name
        boolean is_active
        boolean is_superuser
        timestamp created_at
        timestamp updated_at
    }
    
    ITEMS {
        uuid id PK
        string title
        text description
        decimal price
        uuid owner_id FK
        boolean is_available
        timestamp created_at
        timestamp updated_at
    }
```

## 📋 Tables Overview

### 1. **users** Table

Primary table for user authentication and profile management.

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | User email address |
| `username` | VARCHAR(100) | UNIQUE, NOT NULL | Unique username |
| `hashed_password` | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| `full_name` | VARCHAR(255) | NULL | User's full name |
| `is_active` | BOOLEAN | DEFAULT true | Account active status |
| `is_superuser` | BOOLEAN | DEFAULT false | Admin privileges |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Registration date |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update time |

**Indexes:**
- `idx_users_email` on `email`
- `idx_users_username` on `username`
- `idx_users_is_active` on `is_active`

### 2. **items** Table

Example table for demonstrating CRUD operations and relationships.

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier |
| `title` | VARCHAR(255) | NOT NULL | Item title |
| `description` | TEXT | NULL | Detailed description |
| `price` | DECIMAL(10,2) | DEFAULT 0.00 | Item price |
| `owner_id` | UUID | FOREIGN KEY → users(id) | Owner reference |
| `is_available` | BOOLEAN | DEFAULT true | Availability status |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation date |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update time |

**Indexes:**
- `idx_items_owner_id` on `owner_id`
- `idx_items_is_available` on `is_available`
- `idx_items_created_at` on `created_at`

**Foreign Keys:**
- `fk_items_owner` → `users(id)` ON DELETE CASCADE

## 🔧 SQLAlchemy Models

### User Model (`backend/app/models/user.py`)

```python
from sqlalchemy import Boolean, Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    items = relationship("Item", back_populates="owner", cascade="all, delete-orphan")
```

### Item Model (`backend/app/models/item.py`)

```python
from sqlalchemy import Boolean, Column, String, Text, DECIMAL, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base

class Item(Base):
    __tablename__ = "items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(DECIMAL(10, 2), default=0.00)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="items")
```

## 🔄 Database Migrations

### Alembic Configuration

```python
# alembic/env.py
from app.core.config import settings
from app.core.database import Base
from app.models import *  # Import all models

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
target_metadata = Base.metadata
```

### Creating Migrations

```bash
# Generate migration
alembic revision --autogenerate -m "Add user table"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Initial Migration Example

```python
"""Initial migration

Revision ID: 001
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Create UUID extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), 
                  server_default=sa.text('uuid_generate_v4()'), 
                  nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_superuser', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), 
                  server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), 
                  onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    
    # Create indexes
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_username', 'users', ['username'])

def downgrade():
    op.drop_table('users')
```

## 🔐 Database Security

### Connection Security

```python
# backend/app/core/config.py
class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost/dbname"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30
    
    # SSL Configuration for Production
    DATABASE_SSL_MODE: str = "require"  # disable, allow, prefer, require
```

### User Password Hashing

```python
# backend/app/core/security.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
```

## 📈 Database Optimization

### Query Optimization

1. **Indexes**: Created on frequently queried columns
2. **Lazy Loading**: Relationships use lazy loading by default
3. **Connection Pooling**: SQLAlchemy connection pool configured
4. **Query Pagination**: All list endpoints support pagination

### Performance Settings

```python
# backend/app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,  # Recycle connections after 30 minutes
    echo=False  # Set to True for SQL query logging
)
```

## 🔍 Common Queries

### User Queries

```python
# Get user by email
user = db.query(User).filter(User.email == email).first()

# Get active users
active_users = db.query(User).filter(User.is_active == True).all()

# Get user with items
user_with_items = db.query(User).options(
    joinedload(User.items)
).filter(User.id == user_id).first()
```

### Item Queries

```python
# Get items by owner
items = db.query(Item).filter(Item.owner_id == user_id).all()

# Get available items with pagination
items = db.query(Item).filter(
    Item.is_available == True
).offset(skip).limit(limit).all()

# Get item with owner info
item = db.query(Item).options(
    joinedload(Item.owner)
).filter(Item.id == item_id).first()
```

## 🎯 Best Practices

1. **Use UUIDs**: More secure and scalable than auto-incrementing integers
2. **Timestamps**: Always include created_at and updated_at
3. **Soft Deletes**: Consider using is_active flags instead of hard deletes
4. **Indexes**: Create indexes on foreign keys and frequently queried columns
5. **Constraints**: Use database-level constraints for data integrity
6. **Migrations**: Always use Alembic for schema changes
7. **Connection Pooling**: Configure appropriate pool sizes for your load

---

**Next**: [Backend API Endpoints](Backend-API-Endpoints) →