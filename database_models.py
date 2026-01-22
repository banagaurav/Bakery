from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database import Base
from sqlalchemy.ext.hybrid import hybrid_property

# Enum for User Role
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    SALESMAN = "salesman"
    CUSTOMER = "customer"

# Enum for Working Day Status
class WorkingDayStatus(str, enum.Enum):
    OPEN = "open"
    CLOSE = "close"

# Users Table
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.CUSTOMER)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Items Table
class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    created_by_user = relationship("User", foreign_keys=[created_by])

# Sales Rates Table
class SalesRate(Base):
    __tablename__ = "sales_rates"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    rate = Column(Float, nullable=False)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    customer = relationship("User", foreign_keys=[customer_id])
    item = relationship("Item")
    created_by_user = relationship("User", foreign_keys=[created_by])
    updated_by_user = relationship("User", foreign_keys=[updated_by])

# Stock Assignments Table
class StockAssignment(Base):
    __tablename__ = "stock_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    assignment_date = Column(Date, nullable=False)
    sales_rate_id = Column(Integer, ForeignKey("sales_rates.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    customer = relationship("User", foreign_keys=[customer_id])
    item = relationship("Item")
    sales_rate = relationship("SalesRate", foreign_keys=[sales_rate_id])
    created_by_user = relationship("User", foreign_keys=[created_by]) 

# Production Table
class Production(Base):
    __tablename__ = "production"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    production_date = Column(Date, nullable=False)
    note = Column(String(500), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    item = relationship("Item")
    created_by_user = relationship("User", foreign_keys=[created_by]) 

# Working Days Table
class WorkingDay(Base):
    __tablename__ = "working_days"
    
    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(WorkingDayStatus), nullable=False, default=WorkingDayStatus.OPEN)
    is_working = Column(Boolean, default=True)
    date = Column(Date, nullable=False, unique=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    created_by_user = relationship("User", foreign_keys=[created_by])