from fastapi import APIRouter, Depends, status, Response
from typing import List
from sqlalchemy.orm import Session

from app.schemas.v1 import UserCreate, UserRead
from app.services.user_service import UserService
from app.api.v1.deps import get_db

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, response: Response, db: Session = Depends(get_db)):
    svc = UserService(db)
    user = svc.create_user(payload)
    response.headers["Location"] = f"/api/v1/users/{user.id}"
    return user

@router.get("/", response_model=List[UserRead])
def list_users(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    svc = UserService(db)
    return svc.list_users(skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    svc = UserService(db)
    return svc.get_user(user_id)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    svc = UserService(db)
    svc.delete_user(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
