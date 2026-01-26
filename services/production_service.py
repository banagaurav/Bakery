from typing import Optional
from sqlalchemy.orm import Session, selectinload
from fastapi import HTTPException, status
import database_models
from models import ProductionCreate, ProductionUpdate

class ProductionService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self):
        return self.db.query(database_models.Production)\
            .options(
                selectinload(database_models.Production.item),
                selectinload(database_models.Production.created_by_user)  # ADDED
            )\
            .all()
    
    def get_by_id(self, production_id: int):
        return self.db.query(database_models.Production)\
            .options(
                selectinload(database_models.Production.item),
                selectinload(database_models.Production.created_by_user)  # ADDED
            )\
            .filter(database_models.Production.id == production_id)\
            .first()
    
    def create(self, production_data: ProductionCreate, created_by_user_id: Optional[int] = None):
        # Set created_by if provided
        production_dict = production_data.model_dump()
        if created_by_user_id:
            production_dict['created_by'] = created_by_user_id
        
        production = database_models.Production(**production_dict)
        self.db.add(production)
        self.db.commit()
        self.db.refresh(production)
        
        # Load relationships for response
        production = self.get_by_id(production.id)
        return production
    
    def update(self, production_id: int, production_data: ProductionUpdate):
        production = self.get_by_id(production_id)
        if not production:
            return None
        
        update_data = production_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(production, field, value)
        
        self.db.commit()
        self.db.refresh(production)
        return production
    
    def delete(self, production_id: int):
        production = self.get_by_id(production_id)
        if not production:
            return False
        
        self.db.delete(production)
        self.db.commit()
        return True