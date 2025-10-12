from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.product_repo import ProductRepository
from app.models.models import Product, Tag, OrderItem
from app.schemas.v1 import ProductCreate, ProductUpdate

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
        setattr(product, "tag_names", [t.name for t in product.tags])
        return product

    def get_product(self, product_id: int):
        product = self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        setattr(product, "tag_names", [t.name for t in product.tags])
        return product

    def list_products(self, skip: int = 0, limit: int = 50) -> list[Product]:
        products = self.repo.list(skip=skip, limit=limit)
        for p in products:
            setattr(p, "tag_names", [t.name for t in p.tags])
        return products

    def delete_product(self, product_id: int):
        product = self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if self.db.query(OrderItem).filter(OrderItem.product_id == product.id).first():
            raise HTTPException(
                status_code=400,
                detail="Cannot delete product because it is associated with existing order items"
            )

        self.repo.delete(product)
        self.db.commit()

    def update_product(self, dto: ProductUpdate, product_id: int) -> Product:
        product = self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        if dto.sku:
            product.sku = dto.sku

        if dto.name:
            product.name = dto.name

        if dto.price:
            product.price = dto.price

        if dto.description:
            product.description = dto.description

        if dto.stock:
            product.stock = dto.stock

        if dto.category_id:
            product.category_id = dto.category_id

        if dto.tag_ids:
            tags = self.db.query(Tag).filter(Tag.id.in_(dto.tag_ids)).all()
            product.tags = tags

        self.db.commit()
        self.db.refresh(product)
        setattr(product, "tag_names", [t.name for t in product.tags])
        return product