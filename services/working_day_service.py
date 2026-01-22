from sqlalchemy.orm import Session, selectinload
from fastapi import HTTPException, status
import database_models
from typing import Optional
from models import WorkingDayCreate, WorkingDayUpdate

class WorkingDayService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self):
        return self.db.query(database_models.WorkingDay)\
            .options(selectinload(database_models.WorkingDay.created_by_user))\
            .all()
    
    def get_by_id(self, day_id: int):
        return self.db.query(database_models.WorkingDay)\
            .options(selectinload(database_models.WorkingDay.created_by_user))\
            .filter(database_models.WorkingDay.id == day_id)\
            .first()
    
    def create(self, day_data: WorkingDayCreate, created_by_user_id: Optional[int] = None):
        # Check if working day already exists for this date
        existing_day = self.db.query(database_models.WorkingDay)\
            .filter(database_models.WorkingDay.date == day_data.date)\
            .first()
        
        if existing_day:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Working day already exists for date {day_data.date}"
            )
        
        # Set created_by if provided
        day_dict = day_data.model_dump()
        if created_by_user_id:
            day_dict['created_by'] = created_by_user_id
        
        day = database_models.WorkingDay(**day_dict)
        self.db.add(day)
        self.db.commit()
        self.db.refresh(day)
        
        # Load relationships for response
        day = self.get_by_id(day.id)
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