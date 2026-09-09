# app.py — Bài 6: Tổng hợp CRUD cho resource books
from flask import Flask, jsonify, request

app = Flask(__name__)
app.json.ensure_ascii = False  # Hiển thị tiếng Việt UTF-8

_next = 2  # Bắt đầu từ 2 vì ID=1 đã có sẵn trong danh sách
BOOKS = [{"id": 1, "title": "Clean Code", "author": "R. Martin"}]

def find(bid):
    return next((b for b in BOOKS if b["id"] == bid), None)

# 1. LIST — GET /books (có hỗ trợ query param ?limit=)
@app.route("/books", methods=["GET"])
def list_books():
    n = int(request.args.get("limit", 100))
    return jsonify(BOOKS[:n]), 200

# 2. DETAIL — GET /books/<int:bid>
@app.route("/books/<int:bid>", methods=["GET"])
def get_book(bid):
    book = find(bid)
    if not book:
        return jsonify({"error": "not found"}), 404
    return jsonify(book), 200

# 3. CREATE — POST /books
@app.route("/books", methods=["POST"])
def create_book():
    global _next
    body = request.get_json(silent=True) or {}
    t, a = body.get("title"), body.get("author")
    
    # Validate: bắt buộc phải truyền cả title và author
    if not t or not a:
        return jsonify({"error": "need title+author"}), 400
        
    book = {"id": _next, "title": t, "author": a}
    _next += 1
    BOOKS.append(book)
    return jsonify(book), 201, {"Location": f"/books/{book['id']}"}

# 4 & 5. UPDATE (PUT) & DELETE — /books/<int:bid>
@app.route("/books/<int:bid>", methods=["PUT", "DELETE"])
def modify_book(bid):
    book = find(bid)
    if not book:
        return jsonify({"error": "not found"}), 404

    # Xử lý UPDATE (PUT)
    if request.method == "PUT":
        body = request.get_json(silent=True) or {}
        book.update(body)
        return jsonify(book), 200

    # Xử lý DELETE
    BOOKS.remove(book)
    return "", 204

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)