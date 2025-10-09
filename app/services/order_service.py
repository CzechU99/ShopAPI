from sqlalchemy.orm import Session
from fastapi import HTTPException
from decimal import Decimal

from app.repositories.order_repo import OrderRepository
from app.models.models import Order, OrderItem, Product
from app.schemas.v1 import OrderCreate, OrderItemCreate

class OrderService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = OrderRepository(db)

    def create_order(self, dto: OrderCreate) -> Order:
        with self.db.begin():
            order = Order(user_id=dto.user_id, status="pending", total_amount=Decimal("0.00"))
            self.db.add(order)
            self.db.flush()  

            total = Decimal("0.00")
            for item in dto.items:
                product = self.db.query(Product).filter(Product.id == item.product_id).with_for_update().one_or_none()
                if not product:
                    raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
                if product.stock < item.quantity:
                    raise HTTPException(status_code=409, detail=f"Not enough stock for product {product.id}")
                unit_price = product.price
                total += Decimal(unit_price) * item.quantity

                order_item = OrderItem(order_id=order.id, product_id=product.id, quantity=item.quantity, unit_price=unit_price)
                self.db.add(order_item)

                product.stock = product.stock - item.quantity
                self.db.add(product)

            order.total_amount = total
            self.db.add(order)
        self.db.refresh(order)
        return order

    def get_order(self, order_id: int):
        order = self.repo.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order

    def list_orders(self, skip=0, limit=50):
        return self.repo.list(skip=skip, limit=limit)
