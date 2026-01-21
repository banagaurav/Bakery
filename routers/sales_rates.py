from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date
from dependencies import get_db, get_current_user, require_admin, require_salesman_or_admin
from services.sales_rate_service import SalesRateService
from models import SalesRate, SalesRateCreate, SalesRateUpdate, User

router = APIRouter(prefix="/sales-rates", tags=["sales-rates"])

@router.get("/", response_model=list[SalesRate])
def get_sales_rates(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_salesman_or_admin)
):
    """Get all sales rates"""
    service = SalesRateService(db)
    return service.get_all()

@router.get("/{rate_id}", response_model=SalesRate)
def get_sales_rate(
    rate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_salesman_or_admin)
):
    """Get a specific sales rate by ID"""
    service = SalesRateService(db)
    rate = service.get_by_id(rate_id)
    if not rate:
        raise HTTPException(status_code=404, detail="Sales rate not found")
    return rate

@router.post("/", response_model=SalesRate, status_code=status.HTTP_201_CREATED)
def create_sales_rate(
    rate: SalesRateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new sales rate"""
    service = SalesRateService(db)
    # Match your service method signature - use updated_by_user_id
    return service.create(rate, updated_by_user_id=current_user.id)

@router.put("/{rate_id}", response_model=SalesRate)
def update_sales_rate(
    rate_id: int,
    rate: SalesRateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update a sales rate"""
    service = SalesRateService(db)
    # Match your service method signature - use updated_by_user_id
    updated_rate = service.update(rate_id, rate, updated_by_user_id=current_user.id)
    if not updated_rate:
        raise HTTPException(status_code=404, detail="Sales rate not found")
    return updated_rate

@router.delete("/{rate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sales_rate(
    rate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a sales rate"""
    service = SalesRateService(db)
    # Match your service method signature - use updated_by_user_id
    if not service.delete(rate_id, updated_by_user_id=current_user.id):
        raise HTTPException(status_code=404, detail="Sales rate not found")