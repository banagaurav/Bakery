from sqlalchemy.orm import Session, selectinload
import database_models
from models import SalesRateCreate, SalesRateUpdate

class SalesRateService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self):
        rates = self.db.query(database_models.SalesRate)\
            .options(
                selectinload(database_models.SalesRate.customer),
                selectinload(database_models.SalesRate.item)
            )\
            .all()
        
        # Add names to each rate object
        for rate in rates:
            rate.customer_name = rate.customer.name if rate.customer else None
            rate.item_name = rate.item.name if rate.item else None
        
        return rates
    
    def get_by_id(self, rate_id: int):
        rate = self.db.query(database_models.SalesRate)\
            .options(
                selectinload(database_models.SalesRate.customer),
                selectinload(database_models.SalesRate.item)
            )\
            .filter(database_models.SalesRate.id == rate_id)\
            .first()
        
        if rate:
            # Add names
            rate.customer_name = rate.customer.name if rate.customer else None
            rate.item_name = rate.item.name if rate.item else None
        
        return rate
    
    def get_with_relations(self, rate_id: int):
        """Get sales rate with full customer and item objects"""
        return self.db.query(database_models.SalesRate)\
            .options(
                selectinload(database_models.SalesRate.customer),
                selectinload(database_models.SalesRate.item)
            )\
            .filter(database_models.SalesRate.id == rate_id)\
            .first()
    
    def create(self, rate_data: SalesRateCreate):
        rate = database_models.SalesRate(**rate_data.model_dump())
        self.db.add(rate)
        self.db.commit()
        self.db.refresh(rate)
        return rate
    
    def update(self, rate_id: int, rate_data: SalesRateUpdate):
        rate = self.get_by_id(rate_id)
        if not rate:
            return None
        
        update_data = rate_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rate, field, value)
        
        self.db.commit()
        self.db.refresh(rate)
        return rate
    
    def delete(self, rate_id: int):
        rate = self.db.query(database_models.SalesRate)\
            .filter(database_models.SalesRate.id == rate_id)\
            .first()
        
        if not rate:
            return False
        
        self.db.delete(rate)
        self.db.commit()
        return True
    
    def get_by_customer(self, customer_id: int):
        """Get all sales rates for a specific customer"""
        rates = self.db.query(database_models.SalesRate)\
            .options(selectinload(database_models.SalesRate.item))\
            .filter(database_models.SalesRate.customer_id == customer_id)\
            .all()
        
        for rate in rates:
            rate.item_name = rate.item.name if rate.item else None
        
        return rates
    
    def get_by_item(self, item_id: int):
        """Get all sales rates for a specific item"""
        rates = self.db.query(database_models.SalesRate)\
            .options(selectinload(database_models.SalesRate.customer))\
            .filter(database_models.SalesRate.item_id == item_id)\
            .all()
        
        for rate in rates:
            rate.customer_name = rate.customer.name if rate.customer else None
        
        return rates