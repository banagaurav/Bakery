from sqlalchemy.orm import Session
import database_models
from models import ProductionCreate, ProductionUpdate

class ProductionService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self):
        return self.db.query(database_models.Production).all()
    
    def get_by_id(self, production_id: int):
        return self.db.query(database_models.Production).filter(
            database_models.Production.id == production_id
        ).first()
    
    def create(self, production_data: ProductionCreate):
        production = database_models.Production(**production_data.model_dump())
        self.db.add(production)
        self.db.commit()
        self.db.refresh(production)
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