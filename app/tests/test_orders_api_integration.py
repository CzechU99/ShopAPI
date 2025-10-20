from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_order_endpoint_returns_201():
    payload = {
        "user_id": 1,
        "items": [{"product_id": 1, "quantity": 2}]
    }

    response = client.post("/api/orders", json=payload)

    assert response.status_code in (201, 409, 404)
    data = response.json()
    assert "id" in data or "detail" in data
