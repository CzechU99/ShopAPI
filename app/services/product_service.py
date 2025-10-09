from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.product_repo import ProductRepository
from app.models.models import Product, Tag
from app.schemas.v1 import ProductCreate

class ProductService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProductRepository(db)

    def create_product(self, dto: ProductCreate) -> Product:
        if self.repo.get_by_sku(dto.sku):
            raise HTTPException(status_code=409, detail="Product with this SKU already exists")
        product = Product(
            sku=dto.sku,
            name=dto.name,
            description=dto.description or "",
            price=dto.price,
            stock=dto.stock,
            category_id=dto.category_id
        )
        if dto.tag_ids:
            tags = self.db.query(Tag).filter(Tag.id.in_(dto.tag_ids)).all()
            product.tags = tags
        self.repo.create(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def get_product(self, product_id: int):
        p = self.repo.get_by_id(product_id)
        if not p:
            raise HTTPException(status_code=404, detail="Product not found")
        return p

    def list_products(self, skip=0, limit=50):
        return self.repo.list(skip=skip, limit=limit)

    def delete_product(self, product_id: int):
        p = self.repo.get_by_id(product_id)
        if not p:
            raise HTTPException(status_code=404, detail="Product not found")
        self.repo.delete(p)
        self.db.commit()
