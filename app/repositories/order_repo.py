from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.models import Order

class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, order_id: int) -> Optional[Order]:
        return self.db.query(Order).filter(Order.id == order_id).one_or_none()

    def list(self, skip: int = 0, limit: int = 50) -> List[Order]:
        return self.db.query(Order).offset(skip).limit(limit).all()

    def create(self, order: Order) -> Order:
        self.db.add(order)
        self.db.flush()
        return order
    
    def delete(self, order: Order):
        self.db.delete(order)
