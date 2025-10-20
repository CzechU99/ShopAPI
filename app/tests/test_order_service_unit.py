from unittest.mock import MagicMock
from app.services.order_service import OrderService
from app.schemas.v1 import OrderUpdate, OrderItemUpdate
from app.models.models import Order
from decimal import Decimal

def test_update_order_recalculates_total_correctly():
    mock_repo = MagicMock()
    mock_db = MagicMock()
    service = OrderService(mock_db)
    service.repo = mock_repo

    order = Order(id=1, status="pending", total_amount=Decimal("0.00"))
    mock_repo.get_by_id.return_value = order

    dto = OrderUpdate(
        status="confirmed",
        items=[OrderItemUpdate(product_id=1, quantity=2)]
    )

    mock_db.query().filter().with_for_update().one_or_none.return_value = MagicMock(
        id=1, stock=10, price=Decimal("5.00")
    )

    result = service.update_order(1, dto)

    assert result.status == "confirmed"
    assert result.total_amount == Decimal("10.00")
    mock_db.commit.assert_called_once()
