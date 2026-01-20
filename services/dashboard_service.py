from sqlalchemy.orm import Session
from sqlalchemy import func
import database_models

class DashboardService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_summary(self):
        """Get dashboard summary"""
        return {
            "total_users": self.db.query(database_models.User).count(),
            "total_items": self.db.query(database_models.Item).count(),
            "total_sales_rates": self.db.query(database_models.SalesRate).count(),
            "total_stock_assignments": self.db.query(database_models.StockAssignment).count(),
            "total_production": self.db.query(database_models.Production).count(),
            "total_working_days": self.db.query(database_models.WorkingDay).count(),
        }
    
    def get_production_summary(self):
        """Get production summary by item"""
        result = self.db.query(
            database_models.Production.item_id,
            database_models.Item.name.label('item_name'),
            func.sum(database_models.Production.quantity).label('total_quantity'),
            func.count(database_models.Production.id).label('production_count')
        )\
        .join(database_models.Item)\
        .group_by(database_models.Production.item_id, database_models.Item.name)\
        .all()
        
        return [dict(r._asdict()) for r in result]
    
    def get_sales_summary(self):
        """Get sales summary by customer"""
        result = self.db.query(
            database_models.SalesRate.customer_id,
            database_models.User.name.label('customer_name'),
            func.avg(database_models.SalesRate.rate).label('avg_rate'),
            func.count(database_models.SalesRate.id).label('rate_count')
        )\
        .join(database_models.User)\
        .group_by(database_models.SalesRate.customer_id, database_models.User.name)\
        .all()
        
        return [dict(r._asdict()) for r in result]
    
    def get_stock_summary(self):
        """Get stock summary by customer"""
        result = self.db.query(
            database_models.StockAssignment.customer_id,
            database_models.User.name.label('customer_name'),
            func.sum(database_models.StockAssignment.quantity).label('total_stock'),
            func.count(database_models.StockAssignment.id).label('assignment_count')
        )\
        .join(database_models.User)\
        .group_by(database_models.StockAssignment.customer_id, database_models.User.name)\
        .all()
        
        return [dict(r._asdict()) for r in result]