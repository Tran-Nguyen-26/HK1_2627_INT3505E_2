# app.py — Bài 2: Uniform Interface (Multiple routes & HTTP methods)
from flask import Flask, jsonify, request

app = Flask(__name__)

# GET /health — kiểm tra server còn sống
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

# POST /echo — trả lại đúng dữ liệu JSON client gửi lên
@app.route("/echo", methods=["POST"])
def echo():
    data = request.get_json(silent=True) or {}
    return jsonify({"you_sent": data}), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)