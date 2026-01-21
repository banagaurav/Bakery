# dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Dependency to get current user in any endpoint"""
    from services.auth_service import AuthService
    auth_service = AuthService(db)
    return auth_service.get_current_user(token)

def require_admin(current_user = Depends(get_current_user)):
    """Dependency to require admin role"""
    from models import UserRole
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def require_salesman_or_admin(current_user = Depends(get_current_user)):
    """Dependency to require salesman or admin role"""
    from models import UserRole
    if current_user.role not in [UserRole.ADMIN, UserRole.SALESMAN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Salesman or admin access required"
        )
    return current_user