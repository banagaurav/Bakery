from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import get_db
from services.stock_assignment_service import StockAssignmentService
from models import StockAssignment, StockAssignmentCreate, StockAssignmentUpdate

router = APIRouter(prefix="/stock-assignments", tags=["stock-assignments"])

@router.get("/", response_model=list[StockAssignment])
def get_stock_assignments(db: Session = Depends(get_db)):
    service = StockAssignmentService(db)
    return service.get_all()

@router.get("/{assignment_id}", response_model=StockAssignment)
def get_stock_assignment(assignment_id: int, db: Session = Depends(get_db)):
    service = StockAssignmentService(db)
    assignment = service.get_by_id(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Stock assignment not found")
    return assignment

@router.post("/", response_model=StockAssignment, status_code=status.HTTP_201_CREATED)
def create_stock_assignment(assignment: StockAssignmentCreate, db: Session = Depends(get_db)):
    service = StockAssignmentService(db)
    return service.create(assignment)

@router.put("/{assignment_id}", response_model=StockAssignment)
def update_stock_assignment(assignment_id: int, assignment: StockAssignmentUpdate, db: Session = Depends(get_db)):
    service = StockAssignmentService(db)
    updated_assignment = service.update(assignment_id, assignment)
    if not updated_assignment:
        raise HTTPException(status_code=404, detail="Stock assignment not found")
    return updated_assignment

@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stock_assignment(assignment_id: int, db: Session = Depends(get_db)):
    service = StockAssignmentService(db)
    if not service.delete(assignment_id):
        raise HTTPException(status_code=404, detail="Stock assignment not found")