from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session

from app.schemas.v1 import CategoryRead
from app.models.models import Category
from app.api.v1.deps import get_db

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])

@router.get("/", response_model=List[CategoryRead])
def list_categories(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Category).offset(skip).limit(limit).all()

@router.get("/{category_id}", response_model=CategoryRead)
def get_category(category_id: int, db: Session = Depends(get_db)):
    c = db.query(Category).filter(Category.id == category_id).one_or_none()
    if not c:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Category not found")
    return c
