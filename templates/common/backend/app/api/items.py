from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas import item as item_schema
from app.crud import item as item_crud

router = APIRouter()

@router.post("/", response_model=item_schema.Item)
def create_item(
    item: item_schema.ItemCreate,
    owner_id: int = 1,
    db: Session = Depends(get_db)
):
    return item_crud.create_item(db=db, item=item, owner_id=owner_id)

@router.get("/", response_model=List[item_schema.Item])
def read_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    items = item_crud.get_items(db, skip=skip, limit=limit)
    return items

@router.get("/{item_id}", response_model=item_schema.Item)
def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = item_crud.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@router.put("/{item_id}", response_model=item_schema.Item)
def update_item(
    item_id: int,
    item: item_schema.ItemUpdate,
    db: Session = Depends(get_db)
):
    db_item = item_crud.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item_crud.update_item(db=db, item_id=item_id, item=item)

@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = item_crud.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    item_crud.delete_item(db=db, item_id=item_id)
    return {"message": "Item deleted successfully"}