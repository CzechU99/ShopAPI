from fastapi import APIRouter, Depends, status, Response
from typing import List
from sqlalchemy.orm import Session

from app.schemas.v1 import OrderCreate, OrderRead, OrderUpdate
from app.services.order_service import OrderService
from app.api.v1.deps import get_db

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])

@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate, response: Response, db: Session = Depends(get_db)):
    svc = OrderService(db)
    order = svc.create_order(payload)
    response.headers["Location"] = f"/api/v1/orders/{order.id}"
    return order

@router.get("/", response_model=List[OrderRead])
def list_orders(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    svc = OrderService(db)
    return svc.list_orders(skip=skip, limit=limit)

@router.get("/{order_id}", response_model=OrderRead)
def get_order(order_id: int, db: Session = Depends(get_db)):
    svc = OrderService(db)
    return svc.get_order(order_id)

@router.put("/{order_id}", response_model=OrderRead)
def update_order(order_id: int, payload: OrderUpdate, db: Session = Depends(get_db)):
    svc = OrderService(db)
    order = svc.update_order(order_id, payload)
    return order

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    svc = OrderService(db)
    svc.delete_order(order_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)