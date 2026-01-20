from sqlalchemy.orm import Session,joinedload, selectinload
import database_models
from models import SalesRateCreate, SalesRateUpdate

class SalesRateService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self):
        # Load relationships
        rates = self.db.query(database_models.SalesRate)\
            .options(
                selectinload(database_models.SalesRate.customer),
                selectinload(database_models.SalesRate.item)
            )\
            .all()
        
        # Add names to each rate object
        for rate in rates:
            # These will be included in the Pydantic response
            rate.customer_name = rate.customer.name if rate.customer else None
            rate.item_name = rate.item.name if rate.item else None
        
        return rates
    
    def get_by_id(self, rate_id: int):
        return self.db.query(database_models.SalesRate).filter(
            database_models.SalesRate.id == rate_id
        ).first()
    
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
        rate = self.get_by_id(rate_id)
        if not rate:
            return False
        
        self.db.delete(rate)
        self.db.commit()
        return True