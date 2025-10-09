from fastapi import APIRouter, Depends, status, Response, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.schemas.v1 import UserCreate, UserRead
from app.db.session import SessionLocal
from app.models.models import User

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(prefix="/api/v1/users", tags=["users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, response: Response, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="User with this email already exists")
    user = User(email=payload.email, full_name=payload.full_name, hashed_password=pwd_ctx.hash(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    response.headers["Location"] = f"/api/v1/users/{user.id}"
    return user

@router.get("/", response_model=list[UserRead])
def list_users(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(User).offset(skip).limit(limit).all()
