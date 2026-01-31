from sqlalchemy.orm import Session, selectinload
import database_models
from models import ItemCreate, ItemUpdate
from typing import Optional, List

class ItemService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, item_data: ItemCreate, created_by_user_id: Optional[int] = None):
        # Set created_by if provided
        item_dict = item_data.model_dump()
        if created_by_user_id:
            item_dict['created_by'] = created_by_user_id
        
        item = database_models.Item(**item_dict)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        
        # Load relationships for response
        item = self.get_by_id(item.id)
        return item
    
    def get_all(self):
        return self.db.query(database_models.Item)\
            .options(selectinload(database_models.Item.created_by_user)).all()
    
    def get_by_id(self, item_id: int):
        return self.db.query(database_models.Item)\
            .filter(database_models.Item.id == item_id)\
            .first()
    
    def update(self, item_id: int, item_data: ItemUpdate):
        item = self.get_by_id(item_id)
        if not item:
            return None
        
        update_data = item_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)
        
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def delete(self, item_id: int):
        item = self.get_by_id(item_id)
        if not item:
            return False
        
        self.db.delete(item)
        self.db.commit()
        return True
    
    