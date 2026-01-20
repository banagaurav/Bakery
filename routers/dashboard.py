from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependencies import get_db
from services.dashboard_service import DashboardService
from models import DashboardSummary, ProductionSummary, SalesSummary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Get overall dashboard summary"""
    service = DashboardService(db)
    return service.get_summary()

@router.get("/production-summary")
def get_production_summary(db: Session = Depends(get_db)):
    """Get production summary by item"""
    service = DashboardService(db)
    return service.get_production_summary()

@router.get("/sales-summary")
def get_sales_summary(db: Session = Depends(get_db)):
    """Get sales summary by customer"""
    service = DashboardService(db)
    return service.get_sales_summary()

@router.get("/stock-summary")
def get_stock_summary(db: Session = Depends(get_db)):
    """Get stock assignment summary by customer"""
    service = DashboardService(db)
    return service.get_stock_summary()

@router.get("/stats")
def get_all_stats(db: Session = Depends(get_db)):
    """Get all dashboard statistics in one call"""
    service = DashboardService(db)
    return {
        "summary": service.get_summary(),
        "production_summary": service.get_production_summary(),
        "sales_summary": service.get_sales_summary(),
        "stock_summary": service.get_stock_summary()
    }

@router.get("/recent-activity")
def get_recent_activity(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get recent activity across all tables"""
    service = DashboardService(db)
    
    # You can add more specific recent activity queries here
    # For now, returning empty - you can expand this
    return {
        "recent_users": [],
        "recent_production": [],
        "recent_sales": [],
        "recent_stock": []
    }