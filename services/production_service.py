from sqlalchemy.orm import Session, selectinload
import database_models
from models import ProductionCreate, ProductionUpdate

class ProductionService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self):
        return self.db.query(database_models.Production)\
            .options(selectinload(database_models.Production.item))\
            .all()
    
    def get_by_id(self, production_id: int):
        production = self.db.query(database_models.Production)\
            .options(selectinload(database_models.Production.item))\
            .filter(database_models.Production.id == production_id)\
            .first()
        
        if production:
            production.item_name = production.item.name if production.item else None
        
        return production
    
    def get_with_relations(self, production_id: int):
        """Get production with full item object"""
        return self.db.query(database_models.Production)\
            .options(selectinload(database_models.Production.item))\
            .filter(database_models.Production.id == production_id)\
            .first()
    
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
        production = self.db.query(database_models.Production)\
            .filter(database_models.Production.id == production_id)\
            .first()
        
        if not production:
            return False
        
        self.db.delete(production)
        self.db.commit()
        return True
    
    def get_by_item(self, item_id: int):
        """Get all production records for a specific item"""
        productions = self.db.query(database_models.Production)\
            .filter(database_models.Production.item_id == item_id)\
            .all()
        
        return productions
    
    def get_total_production_by_item(self):
        """Get total production quantity by item"""
        result = self.db.query(
            database_models.Production.item_id,
            database_models.Item.name.label('item_name'),
            database_models.Production.production_date,
            database_models.Production.quantity
        )\
        .join(database_models.Item)\
        .all()
        
        return [dict(r._asdict()) for r in result]