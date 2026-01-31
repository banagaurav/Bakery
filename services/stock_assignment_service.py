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
                selectinload(database_models.StockAssignment.created_by_user)
            )\
            .all()
    
    def get_by_id(self, assignment_id: int):
        return self.db.query(database_models.StockAssignment)\
            .options(
                selectinload(database_models.StockAssignment.customer),
                selectinload(database_models.StockAssignment.item),
                selectinload(database_models.StockAssignment.sales_rate),
                selectinload(database_models.StockAssignment.created_by_user)
            )\
            .filter(database_models.StockAssignment.id == assignment_id)\
            .first()
    
    def create(self, assignment_data: StockAssignmentCreate, created_by_user_id: Optional[int] = None):
        # Convert to dict
        assignment_dict = assignment_data.model_dump()
        
        # Validate customer exists
        customer = self.db.query(database_models.User).filter(
            database_models.User.id == assignment_dict['customer_id']
        ).first()
        
        if not customer:
            raise HTTPException(
                status_code=404,
                detail=f"Customer with ID {assignment_dict['customer_id']} not found"
            )
        
        # Validate item exists
        item = self.db.query(database_models.Item).filter(
            database_models.Item.id == assignment_dict['item_id']
        ).first()
        
        if not item:
            raise HTTPException(
                status_code=404,
                detail=f"Item with ID {assignment_dict['item_id']} not found"
            )
        
        # Handle the manual_rate logic
        manual_rate = assignment_dict.get('manual_rate')
        sales_rate_id = assignment_dict.get('sales_rate_id')
        
        # CASE 1: manual_rate provided
        if manual_rate is not None:
            # Store manual_rate directly in stock_assignments table
            # sales_rate_id should be None when using manual_rate
            assignment_dict['sales_rate_id'] = None
        
        # CASE 2: sales_rate_id provided - validate it exists
        elif sales_rate_id is not None:
            sales_rate = self.db.query(database_models.SalesRate).filter(
                database_models.SalesRate.id == sales_rate_id
            ).first()
            
            if not sales_rate:
                raise HTTPException(
                    status_code=404,
                    detail=f"Sales rate with ID {sales_rate_id} not found"
                )
            
            # Validate it matches customer and item
            if (sales_rate.customer_id != assignment_dict['customer_id'] or 
                sales_rate.item_id != assignment_dict['item_id']):
                raise HTTPException(
                    status_code=400,
                    detail="Sales rate does not match the specified customer and item"
                )
            
            # Ensure manual_rate is None when using sales_rate_id
            assignment_dict['manual_rate'] = None
        
        # CASE 3: Neither provided - look up from existing rates
        else:
            sales_rate = self.get_sales_rate_for_assignment(
                customer_id=assignment_dict['customer_id'],
                item_id=assignment_dict['item_id'],
                assignment_date=assignment_dict['assignment_date']
            )
            
            if sales_rate:
                assignment_dict['sales_rate_id'] = sales_rate.id
                assignment_dict['manual_rate'] = None  # Ensure manual_rate is None
            else:
                # If no sales rate found and no manual rate provided, raise error
                raise HTTPException(
                    status_code=400,
                    detail="No sales rate found and no manual rate provided. Please provide either sales_rate_id or manual_rate."
                )
        
        # Set created_by if provided
        if created_by_user_id:
            assignment_dict['created_by'] = created_by_user_id
        
        # Create the stock assignment
        assignment = database_models.StockAssignment(**assignment_dict)
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        
        # Load relationships for response
        assignment = self.get_by_id(assignment.id)
        return assignment
    
    def get_sales_rate_for_assignment(self, customer_id: int, item_id: int, assignment_date: date):
        """
        Helper method to find the appropriate sales rate for a stock assignment
        """
        return self.db.query(database_models.SalesRate).filter(
            database_models.SalesRate.customer_id == customer_id,
            database_models.SalesRate.item_id == item_id,
            database_models.SalesRate.is_active == True,
            database_models.SalesRate.effective_from <= assignment_date,
            (database_models.SalesRate.effective_to == None) | 
            (database_models.SalesRate.effective_to >= assignment_date)
        ).order_by(
            database_models.SalesRate.effective_from.desc()
        ).first()
    
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