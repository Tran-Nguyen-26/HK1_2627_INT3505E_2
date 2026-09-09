# app.py — Bài 4: Path Parameters & Query Strings
from flask import Flask, jsonify, request

app = Flask(__name__)
app.json.ensure_ascii = False  # Hiển thị tiếng Việt nguyên bản

# Dữ liệu mẫu
BOOKS = [
    {"id": "b1", "title": "Lập trình Python cơ bản", "price": 100},
    {"id": "b2", "title": "Flask RESTful API từ A đến Z", "price": 150},
    {"id": "b3", "title": "Chinh phục Python Nâng Cao", "price": 200},
]

# 1. Query String: Bộ lọc, tìm kiếm, phân trang (/books?q=python&limit=10)
@app.route("/books", methods=["GET"])
def list_books():
    limit = int(request.args.get("limit", 20))
    offset = int(request.args.get("offset", 0))
    q = request.args.get("q", "").strip().lower()

    # Lọc danh sách theo từ khóa `q`
    filtered = [b for b in BOOKS if q in b["title"].lower()]
    
    # Phân trang bằng cắt slice danh sách
    items = filtered[offset : offset + limit]

    return jsonify({
        "total": len(filtered),
        "items": items
    }), 200

# 2. Path Parameter (String): Định danh tài nguyên cụ thể (/books/b1)
@app.route("/books/<book_id>", methods=["GET"])
def get_book(book_id):
    # Tìm sách có id khớp với book_id trên URL
    book = next((b for b in BOOKS if b["id"] == book_id), None)
    
    if book is None:
        return jsonify({"error": "Không tìm thấy sách"}), 404
        
    return jsonify(book), 200

# 3. Path Parameter (Int Converter): Tự động ép kiểu URL sang int (/items/10)
@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    return jsonify({"id": item_id, "type": type(item_id).__name__}), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)