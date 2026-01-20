from sqlalchemy.orm import Session, selectinload
import database_models
from models import ItemCreate, ItemUpdate

class ItemService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self):
        return self.db.query(database_models.Item).all()
    
    def get_by_id(self, item_id: int):
        return self.db.query(database_models.Item)\
            .filter(database_models.Item.id == item_id)\
            .first()
    
    def get_with_relations(self, item_id: int):
        """Get item with all related data"""
        item = self.db.query(database_models.Item)\
            .options(
                selectinload(database_models.Item.sales_rates),
                selectinload(database_models.Item.stock_assignments),
                selectinload(database_models.Item.productions)
            )\
            .filter(database_models.Item.id == item_id)\
            .first()
        
        return item
    
    def create(self, item_data: ItemCreate):
        item = database_models.Item(**item_data.model_dump())
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
    
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
    
    