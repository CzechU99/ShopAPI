from fastapi import APIRouter, Depends, status, Response
from typing import List
from sqlalchemy.orm import Session

from app.schemas.v1 import ProductCreate, ProductRead
from app.services.product_service import ProductService
from app.api.v1.deps import get_db

router = APIRouter(prefix="/api/v1/products", tags=["products"])

@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, response: Response, db: Session = Depends(get_db)):
    svc = ProductService(db)
    product = svc.create_product(payload)
    response.headers["Location"] = f"/api/v1/products/{product.id}"
    return product

@router.get("/", response_model=List[ProductRead])
def list_products(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    svc = ProductService(db)
    return svc.list_products(skip=skip, limit=limit)

@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)):
    svc = ProductService(db)
    return svc.get_product(product_id)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    svc = ProductService(db)
    svc.delete_product(product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
