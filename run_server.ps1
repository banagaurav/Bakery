# run_server.ps1
Write-Host "Starting Bakery Management System..." -ForegroundColor Cyan

# Create main.py if it doesn't exist
$mainFile = "main.py"
if (-not (Test-Path $mainFile)) {
    Write-Host "Creating main.py..." -ForegroundColor Yellow
    @"
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import database_models

# Import routers
try:
    from routers.auth import router as auth_router
    from routers.users import router as users_router
    from routers.items import router as items_router
    from routers.sales_rates import router as sales_rates_router
    from routers.stock_assignments import router as stock_assignments_router
    from routers.production import router as production_router
    from routers.working_days import router as working_days_router
except ImportError as e:
    print(f"Import error: {e}")
    # Create dummy routers for testing
    from fastapi import APIRouter
    auth_router = APIRouter()
    users_router = APIRouter()
    items_router = APIRouter()
    sales_rates_router = APIRouter()
    stock_assignments_router = APIRouter()
    production_router = APIRouter()
    working_days_router = APIRouter()

# Create tables
try:
    database_models.Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database error: {e}")

app = FastAPI(title="Bakery Management System")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "https://25b36840-3b33-456f-bd2b-ecb6afa44a82.lovableproject.com",
        "https://*.ngrok-free.app",
        "http://*.ngrok-free.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/test")
def test():
    return {"status": "API is working!"}
"@ | Out-File -FilePath $mainFile -Encoding utf8
}

# Check what files exist
Write-Host "Files in directory:" -ForegroundColor Green
dir *.py

# Try different possible filenames
$files = @("main.py", "app.py", "server.py", "api.py")
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "Found $file, trying to run..." -ForegroundColor Yellow
        $module = $file.Replace(".py", "")
        python -m uvicorn ${module}:app --host 0.0.0.0 --port 8000 --reload
        break
    }
}