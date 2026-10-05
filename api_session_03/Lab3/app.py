import json
import logging
import base64

from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

PROBLEM_JSON = "application/problem+json"


class ProblemError(Exception):
    """Exception nghiệp vụ, sẽ được trả về dạng problem+json."""
    def __init__(self, status, title, detail=None, type_="about:blank", **extra):
        super().__init__(title)
        self.status = status
        self.title = title
        self.detail = detail
        self.type = type_
        self.extra = extra


def problem_response(status, title, detail, type_="about:blank", extra=None):
    body = {
        "type": type_,
        "title": title,
        "status": status,
        "detail": detail,
        "instance": request.path,
    }
    body.update(extra or {})
    return app.response_class(
        json.dumps(body, ensure_ascii=False),
        status=status,
        mimetype=PROBLEM_JSON
    )


@app.errorhandler(ProblemError)
def handle_problem(e):
    return problem_response(e.status, e.title, e.detail, e.type, e.extra)


@app.errorhandler(HTTPException)
def handle_http_exception(e):
    return problem_response(e.code, e.name, e.description)


@app.errorhandler(Exception)
def handle_unexpected(e):
    log.exception("Unhandled exception at %s %s", request.method, request.path)
    return problem_response(
        500, "Internal Server Error", "Đã xảy ra lỗi phía máy chủ. Vui lòng thử lại sau."
    )


MOCK_ORDERS = [
    {"id": 1, "customer_id": 101, "status": "paid", "total": 150.0},
    {"id": 2, "customer_id": 102, "status": "pending", "total": 200.0},
    {"id": 3, "customer_id": 101, "status": "paid", "total": 50.0},
    {"id": 4, "customer_id": 103, "status": "shipped", "total": 300.0},
    {"id": 5, "customer_id": 104, "status": "paid", "total": 120.0},
    {"id": 6, "customer_id": 101, "status": "cancelled", "total": 40.0},
    {"id": 7, "customer_id": 105, "status": "pending", "total": 500.0},
]

def encode_cursor(order_id):
    """Mã hóa ID thành chuỗi Base64 làm cursor."""
    return base64.urlsafe_b64encode(str(order_id).encode()).decode()

def decode_cursor(cursor_str):
    """Giải mã cursor lấy lại ID. Ném 400 nếu cursor hỏng."""
    try:
        return int(base64.urlsafe_b64decode(cursor_str).decode())
    except Exception:
        raise ProblemError(
            status=400,
            title="Invalid Cursor",
            detail="Giá trị cursor không hợp lệ hoặc đã bị hỏng.",
            type_="https://example.com/problems/invalid-cursor"
        )

@app.get("/orders")
def get_orders():
    # Khởi tạo query từ danh sách gốc
    query = MOCK_ORDERS.copy()

    # 1. LỌC (Filter)
    status = request.args.get("status")
    if status:
        query = [o for o in query if o["status"] == status]
        
    customer_id = request.args.get("customer_id")
    if customer_id and customer_id.isdigit():
        query = [o for o in query if o["customer_id"] == int(customer_id)]

    # 2. SẮP XẾP (Sort)
    # Hỗ trợ dấu '-' ở đầu để xếp giảm dần (VD: sort=-total)
    sort_by = request.args.get("sort", "id")
    reverse = sort_by.startswith("-")
    sort_key = sort_by.lstrip("-")
    
    if sort_key in ["id", "customer_id", "status", "total"]:
        query.sort(key=lambda x: x[sort_key], reverse=reverse)

    # 3. PHÂN TRANG BẰNG CURSOR (Cursor Pagination)
    cursor_str = request.args.get("cursor")
    limit = request.args.get("limit", 3, type=int)
    start_idx = 0

    if cursor_str:
        last_id = decode_cursor(cursor_str)
        # Tìm vị trí của item chứa last_id để cắt mảng từ vị trí tiếp theo
        for i, order in enumerate(query):
            if order["id"] == last_id:
                start_idx = i + 1
                break
                
    paginated_orders = query[start_idx : start_idx + limit]

    # Tạo next_cursor nếu vẫn còn dữ liệu
    next_cursor = None
    if start_idx + limit < len(query):
        next_cursor = encode_cursor(paginated_orders[-1]["id"])

    # 4. SPARSE FIELDSETS
    fields_str = request.args.get("fields")
    if fields_str:
        fields = set(fields_str.split(","))
        result_data = [
            {k: v for k, v in order.items() if k in fields}
            for order in paginated_orders
        ]
    else:
        result_data = paginated_orders

    return jsonify({
        "data": result_data,
        "meta": {
            "limit": limit,
            "next_cursor": next_cursor
        }
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)