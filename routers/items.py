from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import get_db
from services.item_service import ItemService
from models import Item, ItemCreate, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/", response_model=list[Item])
def get_items(db: Session = Depends(get_db)):
    service = ItemService(db)
    return service.get_all()

@router.get("/{item_id}", response_model=Item)
def get_item(item_id: int, db: Session = Depends(get_db)):
    service = ItemService(db)
    item = service.get_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    service = ItemService(db)
    return service.create(item)

@router.put("/{item_id}", response_model=Item)
def update_item(item_id: int, item: ItemUpdate, db: Session = Depends(get_db)):
    service = ItemService(db)
    updated_item = service.update(item_id, item)
    if not updated_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated_item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    service = ItemService(db)
    if not service.delete(item_id):
        raise HTTPException(status_code=404, detail="Item not found")
    