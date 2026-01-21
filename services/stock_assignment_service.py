from sqlalchemy.orm import Session, selectinload
import database_models
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
        assignment = database_models.StockAssignment(**assignment_data.model_dump())
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
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