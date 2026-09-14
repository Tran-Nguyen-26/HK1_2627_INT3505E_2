from flask import Flask, jsonify, request

app = Flask(__name__)
app.json.ensure_ascii = False

_next = 2
BOOKS = [{"id": 1, "title": "Clean Code", "author": "R. Martin"}]


def find(bid):
  return next((b for b in BOOKS if b["id"] == bid), None)


# GỘP PUT VÀ DELETE TRÊN CÙNG ROUTE /books/<int:bid>
@app.route("/books/<int:bid>", methods=["PUT", "DELETE"])
def modify_book(bid):
  book = find(bid)

  # 1. Kiểm tra 404 chung cho cả PUT và DELETE
  if not book:
    return jsonify({"error": "not found"}), 404

  # 2. Rẽ nhánh xử lý phương thức PUT
  if request.method == "PUT":
    body = request.get_json(silent=True) or {}
    book.update(body)
    return jsonify(book), 200

  # 3. Xử lý phương thức DELETE (khi request.method == "DELETE")
  BOOKS.remove(book)
  return "", 204


if __name__ == "__main__":
  app.run(host="127.0.0.1", port=5000, debug=True)