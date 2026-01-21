from pydantic import BaseModel, ConfigDict, computed_field,field_validator, model_validator
from typing import Optional, List
from datetime import date, datetime
import enum

# Enums (redefine for Pydantic)
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    SALESMAN = "salesman"
    CUSTOMER = "customer"

class WorkingDayStatus(str, enum.Enum):
    OPEN = "open"
    CLOSE = "close"

# ========== User Schemas ==========
class UserBase(BaseModel):
    name: str
    role: UserRole = UserRole.CUSTOMER

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[UserRole] = None

class User(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime

# ========== Item Schemas ==========
class ItemBase(BaseModel):
    name: str

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = None

class Item(ItemBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime

# ========== Sales Rate Schemas ==========
class SalesRateBase(BaseModel):
    customer_id: int
    item_id: int
    rate: float
    effective_from: date
    effective_to: Optional[date] = None
    is_active: bool = True

class SalesRateCreate(SalesRateBase):
    @model_validator(mode='after')
    def validate_effective_dates(self):
        if self.effective_to and self.effective_to < self.effective_from:
            raise ValueError("effective_to must be after effective_from")
        return self

class SalesRateUpdate(BaseModel):
    rate: Optional[float] = None
    effective_to: Optional[date] = None
    is_active: Optional[bool] = None

class SalesRate(SalesRateBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    customer: Optional[User] = None  # ADDED
    item: Optional[Item] = None      # ADDED

class SalesRateNonNested(BaseModel): #for stockAssignment 
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    rate: float
    effective_from: date
    effective_to: Optional[date] = None
    is_active: bool
    created_at: datetime

# ========== Stock Assignment Schemas ==========
class StockAssignmentBase(BaseModel):
    customer_id: int
    item_id: int
    quantity: int
    assignment_date: date

class StockAssignmentCreate(StockAssignmentBase):
    sales_rate_id: Optional[int] = None 

class StockAssignmentUpdate(BaseModel):
    quantity: Optional[int] = None
    rate: Optional[float] = None

class StockAssignment(StockAssignmentBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    customer: Optional[User] = None  # ADDED
    item: Optional[Item] = None      # ADDED
    sales_rate: Optional[SalesRateNonNested] = None
    # Computed field
    @computed_field
    @property
    def total_price(self) -> float:
        if self.sales_rate and hasattr(self, 'quantity'):
            return self.quantity * self.sales_rate.rate
        return 0.0
    
    @computed_field
    @property
    def rate(self) -> Optional[float]:
        return self.sales_rate.rate if self.sales_rate else None


# ========== Production Schemas ==========
class ProductionBase(BaseModel):
    item_id: int
    quantity: int
    production_date: date
    note: Optional[str] = None

class ProductionCreate(ProductionBase):
    pass

class ProductionUpdate(BaseModel):
    quantity: Optional[int] = None
    production_date: Optional[date] = None
    note: Optional[str] = None

class Production(ProductionBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    item: Optional[Item] = None  # Add this

# ========== Working Day Schemas ==========
class WorkingDayBase(BaseModel):
    status: WorkingDayStatus = WorkingDayStatus.OPEN
    is_working: bool = True
    date: date

class WorkingDayCreate(WorkingDayBase):
    pass

class WorkingDayUpdate(BaseModel):
    status: Optional[WorkingDayStatus] = None
    is_working: Optional[bool] = None

class WorkingDay(WorkingDayBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime

# ========== Response with Relationships ==========
class UserWithRelations(User):
    sales_rates: List[SalesRate] = []
    stock_assignments: List[StockAssignment] = []

class ItemWithRelations(Item):  # Changed from ProductWithRelations to ItemWithRelations
    sales_rates: List[SalesRate] = []
    stock_assignments: List[StockAssignment] = []
    productions: List[Production] = []