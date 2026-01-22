from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import get_db, get_current_user  # ADD get_current_user
from services.sales_rate_service import SalesRateService
from models import SalesRate, SalesRateCreate, SalesRateUpdate
from database_models import User  # ADD this import

router = APIRouter(prefix="/sales-rates", tags=["sales-rates"])

@router.get("/", response_model=list[SalesRate])
def get_sales_rates(db: Session = Depends(get_db)):
    service = SalesRateService(db)
    return service.get_all()

@router.get("/{rate_id}", response_model=SalesRate)
def get_sales_rate(rate_id: int, db: Session = Depends(get_db)):
    service = SalesRateService(db)
    rate = service.get_by_id(rate_id)
    if not rate:
        raise HTTPException(status_code=404, detail="Sales rate not found")
    return rate

@router.post("/", response_model=SalesRate, status_code=status.HTTP_201_CREATED)
def create_sales_rate(
    rate: SalesRateCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ADD this
):
    service = SalesRateService(db)
    # Pass the current user's ID as both created_by and updated_by
    return service.create(rate, created_by_user_id=current_user.id, updated_by_user_id=current_user.id)

@router.put("/{rate_id}", response_model=SalesRate)
def update_sales_rate(
    rate_id: int, 
    rate: SalesRateUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ADD this
):
    service = SalesRateService(db)
    updated_rate = service.update(rate_id, rate, updated_by_user_id=current_user.id)
    if not updated_rate:
        raise HTTPException(status_code=404, detail="Sales rate not found")
    return updated_rate

@router.delete("/{rate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sales_rate(
    rate_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ADD this
):
    service = SalesRateService(db)
    if not service.delete(rate_id, updated_by_user_id=current_user.id):
        raise HTTPException(status_code=404, detail="Sales rate not found")