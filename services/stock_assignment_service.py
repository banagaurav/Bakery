from sqlalchemy.orm import Session, selectinload
from datetime import datetime
import database_models
from sqlalchemy import or_
from fastapi import HTTPException, status
from models import StockAssignmentCreate, StockAssignmentUpdate

class StockAssignmentService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self):
        # Only load what's needed, avoid deep nesting
        return self.db.query(database_models.StockAssignment)\
            .options(
                selectinload(database_models.StockAssignment.customer),
                selectinload(database_models.StockAssignment.item),
                selectinload(database_models.StockAssignment.sales_rate)
                # Don't load sales_rate.customer or sales_rate.item
            )\
            .all()
    
    def get_by_id(self, assignment_id: int):
        assignment = self.db.query(database_models.StockAssignment)\
            .options(
                selectinload(database_models.StockAssignment.customer),
                selectinload(database_models.StockAssignment.item)
            )\
            .filter(database_models.StockAssignment.id == assignment_id)\
            .first()
        
        if assignment:
            assignment.customer_name = assignment.customer.name if assignment.customer else None
            assignment.item_name = assignment.item.name if assignment.item else None
        
        return assignment
    
    def get_with_relations(self, assignment_id: int):
        """Get stock assignment with full customer and item objects"""
        return self.db.query(database_models.StockAssignment)\
            .options(
                selectinload(database_models.StockAssignment.customer),
                selectinload(database_models.StockAssignment.item)
            )\
            .filter(database_models.StockAssignment.id == assignment_id)\
            .first()
    
    def create(self, assignment_data: StockAssignmentCreate):
        # Check if sales_rate_id was provided
        sales_rate_id = assignment_data.sales_rate_id
        
        # If not provided, find active sales rate
        if not sales_rate_id:
            from services.sales_rate_service import SalesRateService
            rate_service = SalesRateService(self.db)
            
            # Get active rate for this customer and item
            active_rate = rate_service.get_active_rate_for_customer_item(
                assignment_data.customer_id,
                assignment_data.item_id
            )
            
            if not active_rate:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"No active sales rate found for customer {assignment_data.customer_id} and item {assignment_data.item_id}"
                )
            
            sales_rate_id = active_rate.id
        else:
            # If sales_rate_id was provided, get the rate from it
            sales_rate = self.db.query(database_models.SalesRate)\
                .filter(database_models.SalesRate.id == sales_rate_id)\
                .first()
            
            if not sales_rate:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Sales rate with ID {sales_rate_id} not found"
                )
            
            rate = sales_rate.rate
        
        # Create the stock assignment
        assignment_dict = assignment_data.model_dump(exclude={'sales_rate_id'})
        assignment = database_models.StockAssignment(
            **assignment_dict,
            sales_rate_id=sales_rate_id,
              # Store the rate at assignment time
        )
        
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        
        # Load relationships for response
        assignment = self.db.query(database_models.StockAssignment)\
            .options(
                selectinload(database_models.StockAssignment.customer),
                selectinload(database_models.StockAssignment.item),
                selectinload(database_models.StockAssignment.sales_rate)
            )\
            .filter(database_models.StockAssignment.id == assignment.id)\
            .first()
        
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
        assignment = self.db.query(database_models.StockAssignment)\
            .filter(database_models.StockAssignment.id == assignment_id)\
            .first()
        
        if not assignment:
            return False
        
        self.db.delete(assignment)
        self.db.commit()
        return True
    
    def get_by_customer(self, customer_id: int):
        """Get all stock assignments for a specific customer"""
        assignments = self.db.query(database_models.StockAssignment)\
            .options(selectinload(database_models.StockAssignment.item))\
            .filter(database_models.StockAssignment.customer_id == customer_id)\
            .all()
        
        for assignment in assignments:
            assignment.item_name = assignment.item.name if assignment.item else None
        
        return assignments
    
    def get_by_item(self, item_id: int):
        """Get all stock assignments for a specific item"""
        assignments = self.db.query(database_models.StockAssignment)\
            .options(selectinload(database_models.StockAssignment.customer))\
            .filter(database_models.StockAssignment.item_id == item_id)\
            .all()
        
        for assignment in assignments:
            assignment.customer_name = assignment.customer.name if assignment.customer else None
        
        return assignments
    
    def get_total_stock_by_customer(self, customer_id: int):
        """Get total stock quantity assigned to a customer"""
        result = self.db.query(
            database_models.StockAssignment.item_id,
            database_models.Item.name.label('item_name'),
            database_models.StockAssignment.rate,
            database_models.StockAssignment.assignment_date,
            database_models.StockAssignment.quantity
        )\
        .join(database_models.Item)\
        .filter(database_models.StockAssignment.customer_id == customer_id)\
        .all()
        
        return [dict(r._asdict()) for r in result]