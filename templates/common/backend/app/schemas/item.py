from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: Optional[float] = None
    is_available: bool = True

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_available: Optional[bool] = None

class ItemInDBBase(ItemBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Item(ItemInDBBase):
    pass