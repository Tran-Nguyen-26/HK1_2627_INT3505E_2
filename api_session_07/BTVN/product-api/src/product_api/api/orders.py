from flask import Blueprint, jsonify, request
from sqlalchemy.orm import selectinload
from ..extensions import db
from ..models.product import Product
from ..models.order import Order, OrderItem
from ..errors import NotFound, OutOfStock
from ..schemas_order import OrderIn, OrderOut

orders_bp = Blueprint("orders", __name__, url_prefix="/api/v1/orders")

# 1. POST /api/v1/orders - Tạo đơn hàng (Chứa nhiều sản phẩm)
@orders_bp.post("")
def create_order():
    body = OrderIn().load(request.json)
    items_data = body["items"]

    total_price = 0
    order_items = []

    try:
        for item_data in items_data:
            p_id = item_data["product_id"]
            qty = item_data["qty"]

            p = db.session.get(Product, p_id)
            if not p or p.archived:
                raise NotFound(message=f"Product with id {p_id} not found")

            if p.qty_in_stock < qty:
                raise OutOfStock(message=f"Product '{p.name}' out of stock. Available: {p.qty_in_stock}, requested: {qty}")

            # Trừ số lượng tồn kho
            p.qty_in_stock -= qty

            # Tính giá dòng và cộng tổng đơn
            item_total = p.price_cents * qty
            total_price += item_total

            # Khởi tạo OrderItem
            order_item = OrderItem(
                product_id=p.id,
                qty=qty,
                unit_price_cents=p.price_cents
            )
            order_items.append(order_item)

        # Lưu Order Master
        order = Order(
            total_price_cents=total_price,
            items=order_items
        )
        db.session.add(order)
        db.session.commit()

        # Query lại bằng selectinload để trả về JSON đầy đủ
        stmt = db.select(Order).options(
            selectinload(Order.items).selectinload(OrderItem.product)
        ).where(Order.id == order.id)
        saved_order = db.session.execute(stmt).scalar_one()

        return jsonify(OrderOut().dump(saved_order)), 201

    except Exception:
        db.session.rollback()
        raise

# 2. GET /api/v1/orders - Danh sách đơn hàng (Eager loading chống N+1)
@orders_bp.get("")
def list_orders():
    page = max(1, int(request.args.get("page", 1)))
    size = min(100, max(1, int(request.args.get("size", 20))))

    stmt = (
        db.select(Order)
        .options(selectinload(Order.items).selectinload(OrderItem.product))
        .order_by(Order.id.desc())
        .offset((page - 1) * size)
        .limit(size)
    )

    rows = db.session.execute(stmt).scalars().all()
    total = db.session.scalar(db.select(db.func.count()).select_from(Order))

    return jsonify({
        "items": [OrderOut().dump(o) for o in rows],
        "page": page,
        "size": size,
        "total": total
    }), 200

# 3. GET /api/v1/orders/<int:id> - Xem chi tiết 1 đơn hàng
@orders_bp.get("/<int:id>")
def get_order(id):
    stmt = (
        db.select(Order)
        .options(selectinload(Order.items).selectinload(OrderItem.product))
        .where(Order.id == id)
    )
    order = db.session.execute(stmt).scalar_one_or_none()
    if not order:
        raise NotFound(message=f"Order with id {id} not found")

    return jsonify(OrderOut().dump(order)), 200
