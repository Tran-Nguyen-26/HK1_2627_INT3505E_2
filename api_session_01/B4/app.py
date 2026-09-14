from flask import Flask, jsonify

app = Flask(__name__)
app.json.ensure_ascii = False

# Giả lập Database với dữ liệu mẫu
ORDERS = {
    "ord-1": {"status": "pending", "item": "Laptop"},
    "ord-2": {"status": "shipped", "item": "Điện thoại"},
}


# DELETE /orders/<order_id>
@app.route("/orders/<order_id>", methods=["DELETE"])
def delete_order(order_id):
  order = ORDERS.get(order_id)

  # 1. 404 Not Found — Không tìm thấy đơn hàng
  if order is None:
    return jsonify({"error": "Không tìm thấy đơn hàng"}), 404

  # 2. 409 Conflict — Lỗi nghiệp vụ (Đã giao/Đang vận chuyển thì không cho xóa)
  if order["status"] in ("shipped", "delivered"):
    return (
        jsonify({
            "error": "Không thể xóa đơn hàng đã vận chuyển hoặc đã giao thành công"
        }),
        409,
    )

  # 3. Xóa đơn hàng khỏi Database
  ORDERS.pop(order_id, None)

  # 4. 204 No Content — Xóa thành công, không trả về body
  return "", 204


if __name__ == "__main__":
  app.run(host="127.0.0.1", port=5000, debug=True)