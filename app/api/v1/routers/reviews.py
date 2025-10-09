from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session

from app.schemas.v1 import ReviewRead
from app.models.models import Review
from app.api.v1.deps import get_db

router = APIRouter(prefix="/api/v1/reviews", tags=["reviews"])

@router.get("/", response_model=List[ReviewRead])
def list_reviews(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Review).offset(skip).limit(limit).all()

@router.get("/{review_id}", response_model=ReviewRead)
def get_review(review_id: int, db: Session = Depends(get_db)):
    r = db.query(Review).filter(Review.id == review_id).one_or_none()
    if not r:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Review not found")
    return r
