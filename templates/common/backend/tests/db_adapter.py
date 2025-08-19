"""
Database adapter for tests - wraps sync session to work with async endpoints
"""
from typing import Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.sql import Select
from contextlib import asynccontextmanager


class AsyncSessionAdapter:
    """Adapter to make sync Session work with async code in tests"""
    
    def __init__(self, sync_session: Session):
        self.sync_session = sync_session
    
    async def execute(self, statement: Any):
        """Execute a statement synchronously but return as if it was async"""
        return self.sync_session.execute(statement)
    
    async def commit(self):
        """Commit synchronously but return as if it was async"""
        self.sync_session.commit()
    
    async def rollback(self):
        """Rollback synchronously but return as if it was async"""
        self.sync_session.rollback()
    
    async def refresh(self, instance):
        """Refresh synchronously but return as if it was async"""
        self.sync_session.refresh(instance)
    
    def add(self, instance):
        """Add instance to session"""
        self.sync_session.add(instance)
    
    async def close(self):
        """Close synchronously but return as if it was async"""
        self.sync_session.close()
    
    def __getattr__(self, name):
        """Forward any other attributes to the sync session"""
        return getattr(self.sync_session, name)


@asynccontextmanager
async def get_async_test_db(sync_db: Session):
    """Convert sync session to async-like session for tests"""
    async_session = AsyncSessionAdapter(sync_db)
    try:
        yield async_session
    finally:
        pass  # Session cleanup is handled by the fixture