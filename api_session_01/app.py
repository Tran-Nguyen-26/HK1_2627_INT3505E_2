# app.py — Bài 1: Hello API
from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    # Trả về Python dict -> Flask tự động chuyển thành JSON (Content-Type: application/json)
    return {"message": "Hello, API!"}

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)