from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import get_db, get_current_user, require_admin
from services.user_service import UserService
from models import User, UserCreate, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=list[User])
def get_users(
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)  # Only admin can see all users
):
    service = UserService(db)
    return service.get_all()

@router.get("/me", response_model=User)
def get_my_profile(current_user = Depends(get_current_user)):
    """Get current user's own profile"""
    return current_user

@router.get("/{user_id}", response_model=User)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Users can see their own profile, admin can see anyone
    if current_user.id != user_id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )
    
    service = UserService(db)
    user = service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)  # Only admin can create users
):
    service = UserService(db)
    return service.create(user)

@router.put("/{user_id}", response_model=User)
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)  # Only admin can update users
):
    service = UserService(db)
    updated_user = service.update(user_id, user)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)  # Only admin can delete users
):
    service = UserService(db)
    if not service.delete(user_id):
        raise HTTPException(status_code=404, detail="User not found")