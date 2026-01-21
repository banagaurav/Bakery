from fastapi import FastAPI
from database import engine
import database_models

# Import routers
from routers.auth import router as auth_router
from routers.users import router as users_router
from routers.items import router as items_router
from routers.sales_rates import router as sales_rates_router
from routers.stock_assignments import router as stock_assignments_router
from routers.production import router as production_router
from routers.working_days import router as working_days_router

# Create tables
database_models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bakery Management System")

# Include all routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(items_router)
app.include_router(sales_rates_router)
app.include_router(stock_assignments_router)
app.include_router(production_router)
app.include_router(working_days_router)

@app.get("/")
def root():
    return {"message": "Bakery Management System API"}