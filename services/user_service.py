# services/user_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import database_models
from models import UserCreate, UserUpdate

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self):
        return self.db.query(database_models.User).all()
    
    def get_by_id(self, user_id: int):
        return self.db.query(database_models.User).filter(
            database_models.User.id == user_id
        ).first()
    
    def get_by_name(self, name: str):
        return self.db.query(database_models.User).filter(
            database_models.User.name == name
        ).first()
    
    def create(self, user_data: UserCreate):
        # Check if user with same name already exists
        existing_user = self.get_by_name(user_data.name)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this name already exists"
            )
        
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
        
        # If updating name, check if it's already taken
        if "name" in update_data and update_data["name"] != user.name:
            existing_user = self.get_by_name(update_data["name"])
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this name already exists"
                )
        
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