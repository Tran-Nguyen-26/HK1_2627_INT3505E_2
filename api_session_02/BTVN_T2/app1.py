import sqlite3
from flask import Flask, jsonify, request, make_response, g

app = Flask(__name__)
DB_NAME = "orders.db"

# —— Cấu hình kết nối SQLite ——
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_NAME)
        # Trả về kết quả dưới dạng Dict thay vì Tuple để dễ jsonify
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    """Khởi tạo bảng orders và chèn dữ liệu mẫu nếu chưa có DB"""
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                amount REAL DEFAULT 0.0,
                status TEXT DEFAULT 'pending'
            )
        """)
        # Kiểm tra nếu bảng trống thì chèn dữ liệu ban đầu
        cursor.execute("SELECT COUNT(*) FROM orders")
        if cursor.fetchone()[0] == 0:
            sample_orders = [
                ("Clean Code", "Robert C. Martin", 45.0, "completed"),
                ("Clean Architecture", "Robert C. Martin", 50.0, "completed"),
                ("1984", "Orwell", 25.0, "pending"),
                ("Animal Farm", "Orwell", 20.0, "shipped"),
            ]
            cursor.executemany(
                "INSERT INTO orders (title, author, amount, status) VALUES (?, ?, ?, ?)",
                sample_orders
            )
            db.commit()

# —— Tham số phân trang ——
DEFAULT_SIZE, MAX_SIZE = 20, 100

# —— GET /orders (list + filter + paginate + HATEOAS) ——
@app.get("/orders")
def list_orders():
    try:
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", DEFAULT_SIZE))
    except ValueError:
        return jsonify(error="page and size must be int"), 400

    page = max(page, 1)
    size = max(min(size, MAX_SIZE), 1)

    # Đọc tham số lọc
    author = request.args.get("author")
    q = (request.args.get("q") or "").strip()

    # Xây dựng câu truy vấn 
    where_clauses = []
    params = []

    if author:
        where_clauses.append("LOWER(author) = LOWER(?)")
        params.append(author)
    if q:
        where_clauses.append("LOWER(title) LIKE ?")
        params.append(f"%{q.lower()}%")

    where_str = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    db = get_db()
    cursor = db.cursor()

    # 1. Đếm tổng số bản ghi thỏa điều kiện
    count_query = f"SELECT COUNT(*) FROM orders{where_str}"
    cursor.execute(count_query, params)
    total = cursor.fetchone()[0]

    # 2. Lấy dữ liệu phân trang (LIMIT & OFFSET)
    offset = (page - 1) * size
    data_query = f"SELECT id, title, author, amount, status FROM orders{where_str} LIMIT ? OFFSET ?"
    cursor.execute(data_query, params + [size, offset])
    rows = cursor.fetchall()

    # Chuyển đổi sqlite3.Row thành dictionary
    items = [dict(row) for row in rows]
    last = (total + size - 1) // size if total > 0 else 1

    # Tạo HATEOAS links giữ nguyên các query params hiện tại
    def build_url(p):
        url = f"/orders?page={p}&size={size}"
        if author:
            url += f"&author={author}"
        if q:
            url += f"&q={q}"
        return url

    links = {
        "self": {"href": build_url(page)},
        "first": {"href": build_url(1)},
        "last": {"href": build_url(max(last, 1))}
    }
    if page > 1:
        links["prev"] = {"href": build_url(page - 1)}
    if offset + size < total:
        links["next"] = {"href": build_url(page + 1)}

    body = {
        "data": items,
        "pagination": {
            "page": page,
            "size": size,
            "total": total,
            "total_pages": last
        },
        "_links": links
    }

    resp = make_response(jsonify(body), 200)
    resp.headers["Cache-Control"] = "public, max-age=30"
    return resp


# —— GET /orders/<oid> (Chi tiết đơn hàng) ——
@app.get("/orders/<int:oid>")
def get_order(oid):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, title, author, amount, status FROM orders WHERE id = ?", (oid,))
    row = cursor.fetchone()

    if row is None:
        return jsonify(error="Order not found"), 404

    item = dict(row)
    body = {
        "data": item,
        "_links": {
            "self": {"href": f"/orders/{oid}"},
            "collection": {"href": "/orders"}
        }
    }
    resp = make_response(jsonify(body), 200)
    resp.headers["Cache-Control"] = "public, max-age=30"
    return resp


if __name__ == "__main__":
    init_db()  # Tự động tạo bảng & dữ liệu mẫu khi khởi chạy
    app.run(debug=True, port=5000)