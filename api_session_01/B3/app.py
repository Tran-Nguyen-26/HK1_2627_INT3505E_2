from uuid import uuid4
from flask import Flask, jsonify, request

app = Flask(__name__)

STUDENTS = []


@app.route("/students", methods=["POST"])
def create_student():
  # 1. Đọc dữ liệu JSON từ request (silent=True tránh crash nếu JSON lỗi)
  body = request.get_json(silent=True) or {}

  # 2. Validate dữ liệu
  name = body.get("name")
  if not name:
    return jsonify({"error": "name là bắt buộc"}), 400

  # 3. Tạo resource mới
  student = {
      "id": str(uuid4()),
      "name": name,
      "gpa": body.get("gpa", 0.0),
  }
  STUDENTS.append(student)

  # 4. Trả về response: (body_json, status_code, headers)
  headers = {"Location": f"/students/{student['id']}"}
  return jsonify(student), 201, headers


if __name__ == "__main__":
  app.run(port=5000, debug=True)