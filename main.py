from fastapi import FastAPI
from database import engine
import database_models
from routers import users, items, sales_rates, stock_assignments, production, working_days

# Create tables
# database_models.Base.metadata.drop_all(bind=engine)
database_models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bakery Management System")

# # Include all routers
app.include_router(users.router)
app.include_router(items.router)
app.include_router(sales_rates.router)
app.include_router(stock_assignments.router)
app.include_router(production.router)
app.include_router(working_days.router)

@app.get("/")
def root():
    return {"message": "Bakery Management System API"}