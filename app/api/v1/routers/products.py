from fastapi import APIRouter, Depends, status, Response, HTTPException
from sqlalchemy.orm import Session

from app.schemas.v1 import ProductCreate, ProductRead
from app.db.session import SessionLocal
from app.models.models import Product

router = APIRouter(prefix="/api/v1/products", tags=["products"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, response: Response, db: Session = Depends(get_db)):
    existing = db.query(Product).filter(Product.sku == payload.sku).one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Product with this SKU already exists")
    p = Product(sku=payload.sku, name=payload.name, description=payload.description or "", price=payload.price, stock=payload.stock)
    db.add(p)
    db.commit()
    db.refresh(p)
    response.headers["Location"] = f"/api/v1/products/{p.id}"
    return p

@router.get("/", response_model=list[ProductRead])
def list_products(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Product).offset(skip).limit(limit).all()
