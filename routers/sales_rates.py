from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import get_db
from services.sales_rate_service import SalesRateService
from models import SalesRate, SalesRateCreate, SalesRateUpdate

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
def create_sales_rate(rate: SalesRateCreate, db: Session = Depends(get_db)):
    service = SalesRateService(db)
    return service.create(rate)

@router.put("/{rate_id}", response_model=SalesRate)
def update_sales_rate(rate_id: int, rate: SalesRateUpdate, db: Session = Depends(get_db)):
    service = SalesRateService(db)
    updated_rate = service.update(rate_id, rate)
    if not updated_rate:
        raise HTTPException(status_code=404, detail="Sales rate not found")
    return updated_rate

@router.delete("/{rate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sales_rate(rate_id: int, db: Session = Depends(get_db)):
    service = SalesRateService(db)
    if not service.delete(rate_id):
        raise HTTPException(status_code=404, detail="Sales rate not found")