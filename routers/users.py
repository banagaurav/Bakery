from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import get_db
from services.user_service import UserService
from models import User, UserCreate, UserUpdate

router = APIRouter(prefix="/users")

@router.get("/", response_model=list[User])
def get_users(db: Session = Depends(get_db)):
    service = UserService(db)
    return service.get_all()

@router.get("/{user_id}", response_model=User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.create(user)

@router.put("/{user_id}", response_model=User)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    service = UserService(db)
    updated_user = service.update(user_id, user)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    service = UserService(db)
    if not service.delete(user_id):
        raise HTTPException(status_code=404, detail="User not found")

@router.get("/{user_id}/summary")
def get_user_summary(user_id: int, db: Session = Depends(get_db)):
    """Get summary for a specific user/customer"""
    from services.dashboard_service import DashboardService
    from services.user_service import UserService
    
    user_service = UserService(db)
    dashboard_service = DashboardService(db)
    
    user = user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get all sales rates for this user
    from services.sales_rate_service import SalesRateService
    sales_service = SalesRateService(db)
    sales_rates = sales_service.get_by_customer(user_id)
    
    # Get all stock assignments for this user
    from services.stock_assignment_service import StockAssignmentService
    stock_service = StockAssignmentService(db)
    stock_assignments = stock_service.get_by_customer(user_id)
    
    total_stock = sum(s.quantity for s in stock_assignments)
    avg_rate = sum(s.rate for s in sales_rates) / len(sales_rates) if sales_rates else 0
    
    return {
        "user": user,
        "total_stock_assigned": total_stock,
        "average_sales_rate": avg_rate,
        "sales_rate_count": len(sales_rates),
        "stock_assignment_count": len(stock_assignments)
    }