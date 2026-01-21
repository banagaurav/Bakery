from datetime import datetime, date
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, or_
import database_models
from models import SalesRateCreate, SalesRateUpdate

class SalesRateService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self):
        return self.db.query(database_models.SalesRate)\
            .options(
                selectinload(database_models.SalesRate.customer),
                selectinload(database_models.SalesRate.item),
                selectinload(database_models.SalesRate.updated_by_user)  # ADDED
            )\
            .all()
    
    def get_by_id(self, rate_id: int):
        return self.db.query(database_models.SalesRate)\
            .options(
                selectinload(database_models.SalesRate.customer),
                selectinload(database_models.SalesRate.item),
                selectinload(database_models.SalesRate.updated_by_user)  # ADDED
            )\
            .filter(database_models.SalesRate.id == rate_id)\
            .first()
    
    def create(self, rate_data: SalesRateCreate, updated_by_user_id: Optional[int] = None):
        # Rule 1: If creating a new active rate, deactivate previous active rates
        if rate_data.is_active:
            self._deactivate_previous_rates(
                rate_data.customer_id, 
                rate_data.item_id,
                rate_data.effective_from,
                updated_by_user_id  # Pass who's making the change
            )
        
        # Set updated_by if provided
        rate_dict = rate_data.model_dump()
        if updated_by_user_id:
            rate_dict['updated_by'] = updated_by_user_id
        
        rate = database_models.SalesRate(**rate_dict)
        self.db.add(rate)
        self.db.commit()
        self.db.refresh(rate)
        
        # Load relationships for response
        rate = self.get_by_id(rate.id)
        return rate
    
    def update(self, rate_id: int, rate_data: SalesRateUpdate, updated_by_user_id: Optional[int] = None):
        rate = self.get_by_id(rate_id)
        if not rate:
            return None
        
        update_data = rate_data.model_dump(exclude_unset=True)
        
        # Set updated_by if provided
        if updated_by_user_id:
            update_data['updated_by'] = updated_by_user_id
        
        # Rule 1: If setting is_active to False, set effective_to to today
        if 'is_active' in update_data and update_data['is_active'] is False:
            update_data['effective_to'] = datetime.now().date()
        
        # Rule 2: If setting is_active to True from False
        elif 'is_active' in update_data and update_data['is_active'] is True:
            # Check if there's already an active rate for this customer-item
            existing_active = self._get_active_rate_for_customer_item(
                rate.customer_id, 
                rate.item_id
            )
            
            # If there's another active rate, deactivate it first
            if existing_active and existing_active.id != rate_id:
                existing_active.is_active = False
                existing_active.effective_to = datetime.now().date()
                existing_active.updated_by = updated_by_user_id  # Track who deactivated
                self.db.add(existing_active)
        
        # Rule 3: If effective_from is being updated on an active rate
        if 'effective_from' in update_data and rate.is_active:
            # Deactivate previous rates from the new effective_from date
            self._deactivate_previous_rates(
                rate.customer_id,
                rate.item_id,
                update_data['effective_from'],
                updated_by_user_id  # Pass who's making the change
            )
        
        # Apply updates
        for field, value in update_data.items():
            setattr(rate, field, value)
        
        self.db.commit()
        self.db.refresh(rate)
        
        # Reload with relationships
        rate = self.get_by_id(rate_id)
        return rate
    
    def delete(self, rate_id: int, updated_by_user_id: Optional[int] = None):
        rate = self.get_by_id(rate_id)
        if not rate:
            return False
        
        # If deleting an active rate, check if we need to reactivate a previous rate
        if rate.is_active:
            # Find the most recent inactive rate before this one
            previous_rate = self.db.query(database_models.SalesRate)\
                .filter(
                    and_(
                        database_models.SalesRate.customer_id == rate.customer_id,
                        database_models.SalesRate.item_id == rate.item_id,
                        database_models.SalesRate.id != rate_id,
                        database_models.SalesRate.is_active == False
                    )
                )\
                .order_by(database_models.SalesRate.effective_from.desc())\
                .first()
            
            if previous_rate:
                # Reactivate the previous rate
                previous_rate.is_active = True
                previous_rate.effective_to = None  # Remove end date
                previous_rate.updated_by = updated_by_user_id  # Track who reactivated
                self.db.add(previous_rate)
        
        self.db.delete(rate)
        self.db.commit()
        return True
    
    # Helper methods
    def _deactivate_previous_rates(self, customer_id: int, item_id: int, effective_from: date, updated_by_user_id: Optional[int] = None):
        """Deactivate any active rates that overlap with the new effective_from date"""
        previous_active_rates = self.db.query(database_models.SalesRate)\
            .filter(
                and_(
                    database_models.SalesRate.customer_id == customer_id,
                    database_models.SalesRate.item_id == item_id,
                    database_models.SalesRate.is_active == True,
                    database_models.SalesRate.effective_from <= effective_from,
                    or_(
                        database_models.SalesRate.effective_to.is_(None),
                        database_models.SalesRate.effective_to >= effective_from
                    )
                )
            )\
            .all()
        
        for prev_rate in previous_active_rates:
            prev_rate.is_active = False
            # Set effective_to to one day before the new rate starts
            prev_rate.effective_to = effective_from
            prev_rate.updated_by = updated_by_user_id  # Track who deactivated
            self.db.add(prev_rate)
    
    def _get_active_rate_for_customer_item(self, customer_id: int, item_id: int):
        """Get currently active rate for customer-item pair"""
        return self.db.query(database_models.SalesRate)\
            .filter(
                and_(
                    database_models.SalesRate.customer_id == customer_id,
                    database_models.SalesRate.item_id == item_id,
                    database_models.SalesRate.is_active == True,
                    database_models.SalesRate.effective_from <= datetime.now().date(),
                    or_(
                        database_models.SalesRate.effective_to.is_(None),
                        database_models.SalesRate.effective_to >= datetime.now().date()
                    )
                )
            )\
            .first()
    
    def get_active_rate_for_date(self, customer_id: int, item_id: int, target_date: date):
        """Get active rate for a specific date"""
        return self.db.query(database_models.SalesRate)\
            .options(selectinload(database_models.SalesRate.updated_by_user))\
            .filter(
                and_(
                    database_models.SalesRate.customer_id == customer_id,
                    database_models.SalesRate.item_id == item_id,
                    database_models.SalesRate.is_active == True,
                    database_models.SalesRate.effective_from <= target_date,
                    or_(
                        database_models.SalesRate.effective_to.is_(None),
                        database_models.SalesRate.effective_to >= target_date
                    )
                )
            )\
            .first()