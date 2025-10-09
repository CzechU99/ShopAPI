from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.models import Product, Tag

class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, product_id: int) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).one_or_none()

    def get_by_sku(self, sku: str) -> Optional[Product]:
        return self.db.query(Product).filter(Product.sku == sku).one_or_none()

    def list(self, skip: int = 0, limit: int = 50) -> List[Product]:
        return self.db.query(Product).offset(skip).limit(limit).all()

    def create(self, product: Product) -> Product:
        self.db.add(product)
        self.db.flush()
        return product

    def delete(self, product: Product):
        self.db.delete(product)
