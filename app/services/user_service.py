from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import HTTPException

from app.repositories.user_repo import UserRepository
from app.models.models import User
from app.schemas.v1 import UserCreate

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)

    def create_user(self, dto: UserCreate) -> User:
        if self.repo.get_by_email(dto.email):
            raise HTTPException(status_code=409, detail="User with this email already exists")
        
        user = User(
            email=dto.email,
            full_name=dto.full_name,
            hashed_password=dto.password
        )
        
        self.repo.create(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def list_users(self, skip=0, limit=50):
        return self.repo.list(skip=skip, limit=limit)

    def get_user(self, user_id: int):
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def delete_user(self, user_id: int):
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        self.repo.delete(user)
        self.db.commit()
