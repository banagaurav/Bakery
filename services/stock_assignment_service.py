from sqlalchemy.orm import Session, selectinload
from fastapi import HTTPException, status
from typing import Optional, List
import database_models
from models import StockAssignmentCreate, StockAssignmentUpdate

class StockAssignmentService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self):
        return self.db.query(database_models.StockAssignment)\
            .options(
                selectinload(database_models.StockAssignment.customer),
                selectinload(database_models.StockAssignment.item),
                selectinload(database_models.StockAssignment.sales_rate),
                selectinload(database_models.StockAssignment.created_by_user)  # ADDED
            )\
            .all()
    
    def get_by_id(self, assignment_id: int):
        return self.db.query(database_models.StockAssignment)\
            .options(
                selectinload(database_models.StockAssignment.customer),
                selectinload(database_models.StockAssignment.item),
                selectinload(database_models.StockAssignment.sales_rate),
                selectinload(database_models.StockAssignment.created_by_user)  # ADDED
            )\
            .filter(database_models.StockAssignment.id == assignment_id)\
            .first()
    
    def create(self, assignment_data: StockAssignmentCreate, created_by_user_id: Optional[int] = None):
        # Set created_by if provided
        assignment_dict = assignment_data.model_dump()
        if created_by_user_id:
            assignment_dict['created_by'] = created_by_user_id
        
        assignment = database_models.StockAssignment(**assignment_dict)
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        
        # Load relationships for response
        assignment = self.get_by_id(assignment.id)
        return assignment
    
    def update(self, assignment_id: int, assignment_data: StockAssignmentUpdate):
        assignment = self.get_by_id(assignment_id)
        if not assignment:
            return None
        
        update_data = assignment_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(assignment, field, value)
        
        self.db.commit()
        self.db.refresh(assignment)
        return assignment
    
    def delete(self, assignment_id: int):
        assignment = self.get_by_id(assignment_id)
        if not assignment:
            return False
        
        self.db.delete(assignment)
        self.db.commit()
        return True