from sqlalchemy.orm import Session
import database_models
from models import WorkingDayCreate, WorkingDayUpdate

class WorkingDayService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self):
        return self.db.query(database_models.WorkingDay).all()
    
    def get_by_id(self, day_id: int):
        return self.db.query(database_models.WorkingDay).filter(
            database_models.WorkingDay.id == day_id
        ).first()
    
    def create(self, day_data: WorkingDayCreate):
        day = database_models.WorkingDay(**day_data.model_dump())
        self.db.add(day)
        self.db.commit()
        self.db.refresh(day)
        return day
    
    def update(self, day_id: int, day_data: WorkingDayUpdate):
        day = self.get_by_id(day_id)
        if not day:
            return None
        
        update_data = day_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(day, field, value)
        
        self.db.commit()
        self.db.refresh(day)
        return day
    
    def delete(self, day_id: int):
        day = self.get_by_id(day_id)
        if not day:
            return False
        
        self.db.delete(day)
        self.db.commit()
        return True