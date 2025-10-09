from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.models import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).one_or_none()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).one_or_none()

    def list(self, skip: int = 0, limit: int = 50) -> List[User]:
        return self.db.query(User).offset(skip).limit(limit).all()

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        return user

    def delete(self, user: User):
        self.db.delete(user)
