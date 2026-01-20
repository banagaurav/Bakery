from sqlalchemy.orm import Session, selectinload
from fastapi import HTTPException, status
import database_models
from models import UserCreate, UserUpdate

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self):
        return self.db.query(database_models.User).all()
    
    def get_by_id(self, user_id: int):
        return self.db.query(database_models.User)\
            .filter(database_models.User.id == user_id)\
            .first()
    
    def get_with_relations(self, user_id: int):
        """Get user with all related data"""
        user = self.db.query(database_models.User)\
            .options(
                selectinload(database_models.User.sales_rates),
                selectinload(database_models.User.stock_assignments)
            )\
            .filter(database_models.User.id == user_id)\
            .first()
        
        return user
    
    def create(self, user_data: UserCreate):
        user = database_models.User(**user_data.model_dump())
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update(self, user_id: int, user_data: UserUpdate):
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete(self, user_id: int):
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        return True