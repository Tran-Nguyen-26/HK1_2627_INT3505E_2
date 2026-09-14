from flask import Flask, jsonify, request

app = Flask(__name__)
app.json.ensure_ascii = False  # Giữ nguyên tiếng Việt/ký tự đặc biệt

# Khởi tạo ID kế tiếp là 3 vì đã có ID 1 và ID 2 trong dữ liệu mẫu
_next = 3
BOOKS = [
    {"id": 1, "title": "Clean Code", "author": "R. Martin"},
    {"id": 2, "title": "Pragmatic Programmer", "author": "Andrew Hunt"},
]


def find(bid):
  """Hàm phụ trợ tìm sách theo ID"""
  return next((b for b in BOOKS if b["id"] == bid), None)


# 1. GET /books — Lấy danh sách tất cả sách
@app.route("/books", methods=["GET"])
def list_books():
  return jsonify(BOOKS), 200


# 2. GET /books/<int:bid> — Lấy chi tiết 1 cuốn sách
@app.route("/books/<int:bid>", methods=["GET"])
def get_book(bid):
  book = find(bid)
  if not book:
    return jsonify({"error": "not found"}), 404
  return jsonify(book), 200


# 3. POST /books — Tạo sách mới (Có Validate)
@app.route("/books", methods=["POST"])
def create_book():
  global _next
  body = request.get_json(silent=True) or {}
  t, a = body.get("title"), body.get("author")

  # Validate: Bắt buộc phải có cả title và author
  if not t or not a:
    return jsonify({"error": "need title+author"}), 400

  book = {"id": _next, "title": t, "author": a}
  _next += 1
  BOOKS.append(book)

  # Trả về 201 Created kèm Header Location
  return jsonify(book), 201, {"Location": f"/books/{book['id']}"}


# 4. PUT & DELETE /books/<int:bid> — Cập nhật & Xóa sách (Gộp Route)
@app.route("/books/<int:bid>", methods=["PUT", "DELETE"])
def modify_book(bid):
  book = find(bid)

  # Trả về 404 nếu không tìm thấy sách
  if not book:
    return jsonify({"error": "not found"}), 404

  # Nhánh xử lý PUT (Update)
  if request.method == "PUT":
    body = request.get_json(silent=True) or {}
    book.update(body)
    return jsonify(book), 200

  # Nhánh xử lý DELETE (Xóa)
  BOOKS.remove(book)
  return "", 204


if __name__ == "__main__":
  app.run(host="127.0.0.1", port=5000, debug=True)