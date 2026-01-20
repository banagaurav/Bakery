from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import get_db
from services.working_day_service import WorkingDayService
from models import WorkingDay, WorkingDayCreate, WorkingDayUpdate

router = APIRouter(prefix="/working-days", tags=["working-days"])

@router.get("/", response_model=list[WorkingDay])
def get_working_days(db: Session = Depends(get_db)):
    service = WorkingDayService(db)
    return service.get_all()

@router.get("/{day_id}", response_model=WorkingDay)
def get_working_day(day_id: int, db: Session = Depends(get_db)):
    service = WorkingDayService(db)
    day = service.get_by_id(day_id)
    if not day:
        raise HTTPException(status_code=404, detail="Working day not found")
    return day

@router.post("/", response_model=WorkingDay, status_code=status.HTTP_201_CREATED)
def create_working_day(day: WorkingDayCreate, db: Session = Depends(get_db)):
    service = WorkingDayService(db)
    return service.create(day)

@router.put("/{day_id}", response_model=WorkingDay)
def update_working_day(day_id: int, day: WorkingDayUpdate, db: Session = Depends(get_db)):
    service = WorkingDayService(db)
    updated_day = service.update(day_id, day)
    if not updated_day:
        raise HTTPException(status_code=404, detail="Working day not found")
    return updated_day

@router.delete("/{day_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_working_day(day_id: int, db: Session = Depends(get_db)):
    service = WorkingDayService(db)
    if not service.delete(day_id):
        raise HTTPException(status_code=404, detail="Working day not found")