import pytest
from sqlalchemy import event
from sqlalchemy.engine import Engine
from product_api.extensions import db
from product_api.models.product import Product

# 1. Test Endpoint POST /api/v1/orders
def test_create_order_post(client):
    # Tạo sản phẩm trước
    res_p = client.post("/api/v1/products", json={
        "sku": "TEST-01",
        "name": "Tai nghe Test",
        "price_cents": 150000,
        "qty_in_stock": 10
    })
    assert res_p.status_code == 201
    product_id = res_p.get_json()["id"]

    # Gọi POST /api/v1/orders
    res_order = client.post("/api/v1/orders", json={
        "items": [
            {"product_id": product_id, "qty": 2}
        ]
    })

    assert res_order.status_code == 201
    data = res_order.get_json()
    assert data["total_price_cents"] == 300000
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == product_id

    # Kiểm tra tồn kho đã bị trừ từ 10 -> 8
    res_p_check = client.get(f"/api/v1/products/{product_id}")
    assert res_p_check.get_json()["qty_in_stock"] == 8


# 2. Test Endpoint GET /api/v1/orders + Kiểm tra N+1 Query bằng Eager Loading (selectinload)
def test_list_orders_get_eager_loading(client, app):
    # Chuẩn bị 3 sản phẩm và 5 đơn hàng với nhiều item khác nhau
    with app.app_context():
        p1 = Product(sku="P1", name="Product 1", price_cents=100, qty_in_stock=100)
        p2 = Product(sku="P2", name="Product 2", price_cents=200, qty_in_stock=100)
        db.session.add_all([p1, p2])
        db.session.commit()

        # Tạo nhiều đơn hàng
        for _ in range(5):
            client.post("/api/v1/orders", json={
                "items": [
                    {"product_id": p1.id, "qty": 1},
                    {"product_id": p2.id, "qty": 2}
                ]
            })

    # Lắng nghe và đếm số lượng SQL Query thực thi trong thời gian gọi GET API
    queries_executed = []

    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        queries_executed.append(statement)

    listener = before_cursor_execute
    event.listen(Engine, "before_cursor_execute", listener)

    try:
        # Gọi GET /api/v1/orders
        response = client.get("/api/v1/orders")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["items"]) == 5

        # KIỂM TRA CHỐNG N+1 QUERY:
        # Với Eager Loading (selectinload), tổng số query chỉ gồm:
        # 1 query đếm total + 1 query select orders + 1 query select order_items + 1 query select products = 4 queries
        # Nếu bị N+1, số query sẽ vọt lên > 15 queries.
        print(f"\n[QUERY COUNT]: Số câu lệnh SQL đã thực thi = {len(queries_executed)}")
        assert len(queries_executed) <= 4, f"Phát hiện lỗi N+1 Query! Số câu query là {len(queries_executed)}"

    finally:
        event.remove(Engine, "before_cursor_execute", listener)
