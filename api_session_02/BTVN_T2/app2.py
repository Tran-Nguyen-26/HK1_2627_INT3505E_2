import hashlib
import json
import sqlite3
from flask import Flask, jsonify, request, make_response, g

app = Flask(__name__)
DB_NAME = "books.db"

# —— Helper tạo ETag từ nội dung dữ liệu ——
def generate_etag(data_dict):
    """Hash MD5 nội dung dữ liệu (JSON) để tạo chuỗi ETag định danh"""
    serialized = json.dumps(data_dict, sort_keys=True).encode("utf-8")
    return f'"{hashlib.md5(serialized).hexdigest()}"'

# —— Cấu hình SQLite ——
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_NAME)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL
            )
        """)
        cursor.execute("SELECT COUNT(*) FROM books")
        if cursor.fetchone()[0] == 0:
            sample_books = [
                ("Clean Code", "Robert C. Martin"),
                ("Clean Architecture", "Robert C. Martin"),
                ("1984", "Orwell"),
                ("Animal Farm", "Orwell"),
            ]
            cursor.executemany("INSERT INTO books (title, author) VALUES (?, ?)", sample_books)
            db.commit()

# —— GET /books/<id> với ETag & If-None-Match ——
@app.get("/books/<int:book_id>")
def get_book(book_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, title, author FROM books WHERE id = ?", (book_id,))
    row = cursor.fetchone()

    if row is None:
        return jsonify(error="Book not found"), 404

    book_data = dict(row)

    # 1. Hash nội dung để sinh ETag
    etag = generate_etag(book_data)

    # 2. Kiểm tra header If-None-Match gửi lên từ Client
    if_none_match = request.headers.get("If-None-Match")

    # 3. Nếu ETag khớp -> Trả về 304 Not Modified (không kèm body)
    if if_none_match and if_none_match == etag:
        resp = make_response("", 304)
        resp.headers["ETag"] = etag
        return resp

    # 4. Nếu ETag không khớp hoặc lần đầu gọi -> Trả về 200 OK + Body + ETag
    body = {
        "data": book_data,
        "_links": {
            "self": {"href": f"/books/{book_id}"},
            "collection": {"href": "/books"}
        }
    }
    resp = make_response(jsonify(body), 200)
    resp.headers["ETag"] = etag
    resp.headers["Cache-Control"] = "no-cache"  # Bắt buộc Client kiểm tra ETag trước khi dùng cache
    return resp

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)