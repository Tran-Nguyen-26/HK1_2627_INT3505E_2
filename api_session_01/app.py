from flask import Flask, jsonify

app = Flask(__name__)
app.json.ensure_ascii = False  # Hỗ trợ hiển thị tiếng Việt UTF-8

# Giả lập Database đơn hàng
ORDERS = {
    "ord_01": {"id": "ord_01", "status": "pending", "item": "Laptop"},
    "ord_02": {"id": "ord_02", "status": "shipped", "item": "Điện thoại"},
}

# DELETE /orders/<order_id>
@app.route("/orders/<order_id>", methods=["DELETE"])
def delete_order(order_id):
    order = ORDERS.get(order_id)

    # 404 Not Found — Không tìm thấy tài nguyên
    if order is None:
        return jsonify({"error": "Không tìm thấy đơn hàng"}), 404

    # 409 Conflict — Vi phạm quy tắc nghiệp vụ (đang/đã giao thì không cho xóa)
    if order["status"] in ("shipped", "delivered"):
        return jsonify({"error": "Không thể xóa đơn hàng đã giao hoặc đang vận chuyển"}), 409

    # Xóa đơn hàng khỏi cơ sở dữ liệu
    ORDERS.pop(order_id, None)

    # 204 No Content — Xóa thành công, không trả về body
    return "", 204

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)