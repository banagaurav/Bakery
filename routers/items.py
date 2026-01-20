from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import get_db
from services.item_service import ItemService
from models import Item, ItemCreate, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/", response_model=list[Item])
def get_items(db: Session = Depends(get_db)):
    service = ItemService(db)
    return service.get_all()

@router.get("/{item_id}", response_model=Item)
def get_item(item_id: int, db: Session = Depends(get_db)):
    service = ItemService(db)
    item = service.get_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    service = ItemService(db)
    return service.create(item)

@router.put("/{item_id}", response_model=Item)
def update_item(item_id: int, item: ItemUpdate, db: Session = Depends(get_db)):
    service = ItemService(db)
    updated_item = service.update(item_id, item)
    if not updated_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated_item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    service = ItemService(db)
    if not service.delete(item_id):
        raise HTTPException(status_code=404, detail="Item not found")
    
@router.get("/{item_id}/summary")
def get_item_summary(item_id: int, db: Session = Depends(get_db)):
    """Get summary for a specific item"""
    from services.dashboard_service import DashboardService
    from services.item_service import ItemService
    
    item_service = ItemService(db)
    dashboard_service = DashboardService(db)
    
    item = item_service.get_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Get all productions for this item
    from services.production_service import ProductionService
    production_service = ProductionService(db)
    productions = production_service.get_by_item(item_id)
    
    # Get all sales rates for this item
    from services.sales_rate_service import SalesRateService
    sales_service = SalesRateService(db)
    sales_rates = sales_service.get_by_item(item_id)
    
    # Get all stock assignments for this item
    from services.stock_assignment_service import StockAssignmentService
    stock_service = StockAssignmentService(db)
    stock_assignments = stock_service.get_by_item(item_id)
    
    total_production = sum(p.quantity for p in productions)
    total_stock_assigned = sum(s.quantity for s in stock_assignments)
    
    return {
        "item": item,
        "total_production": total_production,
        "total_stock_assigned": total_stock_assigned,
        "production_count": len(productions),
        "sales_rate_count": len(sales_rates),
        "stock_assignment_count": len(stock_assignments)
    }