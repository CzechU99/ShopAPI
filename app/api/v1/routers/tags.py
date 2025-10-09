from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session

from app.schemas.v1 import TagRead
from app.models.models import Tag
from app.api.v1.deps import get_db

router = APIRouter(prefix="/api/v1/tags", tags=["tags"])

@router.get("/", response_model=List[TagRead])
def list_tags(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Tag).offset(skip).limit(limit).all()

@router.get("/{tag_id}", response_model=TagRead)
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    t = db.query(Tag).filter(Tag.id == tag_id).one_or_none()
    if not t:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Tag not found")
    return t
