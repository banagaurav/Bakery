from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import get_db
from services.production_service import ProductionService
from models import Production, ProductionCreate, ProductionUpdate

router = APIRouter(prefix="/production", tags=["production"])

@router.get("/", response_model=list[Production])
def get_production_records(db: Session = Depends(get_db)):
    service = ProductionService(db)
    return service.get_all()

@router.get("/{production_id}", response_model=Production)
def get_production_record(production_id: int, db: Session = Depends(get_db)):
    service = ProductionService(db)
    production = service.get_by_id(production_id)
    if not production:
        raise HTTPException(status_code=404, detail="Production record not found")
    return production

@router.post("/", response_model=Production, status_code=status.HTTP_201_CREATED)
def create_production_record(production: ProductionCreate, db: Session = Depends(get_db)):
    service = ProductionService(db)
    return service.create(production)

@router.put("/{production_id}", response_model=Production)
def update_production_record(production_id: int, production: ProductionUpdate, db: Session = Depends(get_db)):
    service = ProductionService(db)
    updated_production = service.update(production_id, production)
    if not updated_production:
        raise HTTPException(status_code=404, detail="Production record not found")
    return updated_production

@router.delete("/{production_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_production_record(production_id: int, db: Session = Depends(get_db)):
    service = ProductionService(db)
    if not service.delete(production_id):
        raise HTTPException(status_code=404, detail="Production record not found")