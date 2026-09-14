from flask import Flask, jsonify, request

app = Flask(__name__)
app.json.ensure_ascii = False  # Hỗ trợ hiển thị tiếng Việt nguyên bản

# Dữ liệu mẫu ban đầu
_next_id = 3
BOOKS = [
    {
        "id": 1,
        "title": "Clean Code",
        "author": "R. Martin",
        "year": 2008,
    },
    {
        "id": 2,
        "title": "Pragmatic Programmer",
        "author": "Andrew Hunt",
        "year": 1999,
    },
]


def find_book(bid):
  """Hàm phụ trợ tìm sách theo ID"""
  return next((b for b in BOOKS if b["id"] == bid), None)


# -------------------------------------------------------------------
# 1. GET /books — Lấy danh sách, Tìm kiếm (?q=), Sắp xếp (?sort=title)
# -------------------------------------------------------------------
@app.route("/books", methods=["GET"])
def list_books():
  q = request.args.get("q", "").strip().lower()
  sort_by = request.args.get("sort", "").strip().lower()

  # Lọc theo từ khóa q (tìm trong title hoặc author)
  result = BOOKS
  if q:
    result = [
        b
        for b in result
        if q in b["title"].lower() or q in b["author"].lower()
    ]

  # Sắp xếp theo title nếu ?sort=title
  if sort_by == "title":
    result = sorted(result, key=lambda x: x["title"].lower())

  return jsonify(result), 200


# -------------------------------------------------------------------
# 2. GET /books/<int:bid> — Lấy chi tiết 1 cuốn sách
# -------------------------------------------------------------------
@app.route("/books/<int:bid>", methods=["GET"])
def get_book(bid):
  book = find_book(bid)
  if not book:
    return jsonify({"error": "not found"}), 404
  return jsonify(book), 200


# -------------------------------------------------------------------
# 3. POST /books — Tạo sách mới (Validate year >= 1900)
# -------------------------------------------------------------------
@app.route("/books", methods=["POST"])
def create_book():
  global _next_id
  body = request.get_json(silent=True) or {}

  title = body.get("title")
  author = body.get("author")
  year = body.get("year")

  # Kiểm tra các trường bắt buộc
  if not title or not author or year is None:
    return (
        jsonify({"error": "Bắt buộc phải nhập đầy đủ 'title', 'author', 'year'"}),
        400,
    )

  # Validate: year phải là số nguyên và >= 1900
  if (
      not isinstance(year, int)
      or isinstance(year, bool)
      or year < 1900
  ):
    return (
        jsonify({"error": "Trường 'year' phải là số nguyên lớn hơn hoặc bằng 1900"}),
        422,
    )

  book = {
      "id": _next_id,
      "title": str(title).strip(),
      "author": str(author).strip(),
      "year": year,
  }

  _next_id += 1
  BOOKS.append(book)

  return jsonify(book), 201, {"Location": f"/books/{book['id']}"}


# -------------------------------------------------------------------
# 4. PUT & DELETE /books/<int:bid> — Cập nhật & Xóa sách
# -------------------------------------------------------------------
@app.route("/books/<int:bid>", methods=["PUT", "DELETE"])
def modify_book(bid):
  book = find_book(bid)
  if not book:
    return jsonify({"error": "not found"}), 404

  # Xử lý PUT (Cập nhật)
  if request.method == "PUT":
    body = request.get_json(silent=True) or {}

    # Nếu có cập nhật field year -> Validate
    if "year" in body:
      year = body["year"]
      if (
          not isinstance(year, int)
          or isinstance(year, bool)
          or year < 1900
      ):
        return (
            jsonify(
                {"error": "Trường 'year' phải là số nguyên lớn hơn hoặc bằng 1900"}
            ),
            422,
        )
      book["year"] = year

    if "title" in body:
      book["title"] = str(body["title"]).strip()
    if "author" in body:
      book["author"] = str(body["author"]).strip()

    return jsonify(book), 200

  # Xử lý DELETE (Xóa)
  BOOKS.remove(book)
  return "", 204


if __name__ == "__main__":
  app.run(host="127.0.0.1", port=5000, debug=True)