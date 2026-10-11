from flask import Flask, jsonify, request
import yaml
import os
import uuid
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

# Đọc file openapi.yaml
YAML_PATH = os.path.join(os.path.dirname(__file__), 'openapi.yaml')

# Mock database
tasks_db = {
    "123e4567-e89b-12d3-a456-426614174000": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "title": "Học Swagger UI",
        "status": "in_progress",
        "priority": "high"
    }
}

@app.route('/openapi.json')
def openapi_json():
    with open(YAML_PATH, 'r', encoding='utf-8') as file:
        spec = yaml.safe_load(file)
    return jsonify(spec)

# Cấu hình Swagger UI
SWAGGER_URL = '/docs'
API_URL = '/openapi.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Tasks API"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# --- Các Endpoints ---

@app.route('/v1/tasks', methods=['GET'])
def list_tasks():
    limit = int(request.args.get('limit', 10))
    return jsonify(list(tasks_db.values())[:limit]), 200

@app.route('/v1/tasks', methods=['POST'])
def create_task():
    data = request.json or {}
    if 'title' not in data:
        return jsonify({"status": 422, "message": "Thiếu thông tin title"}), 422
    
    new_id = str(uuid.uuid4())
    new_task = {
        "id": new_id,
        "title": data['title'],
        "status": "open",
        "priority": data.get('priority', 'normal')
    }
    tasks_db[new_id] = new_task
    return jsonify(new_task), 201

@app.route('/v1/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    task = tasks_db.get(task_id)
    if not task:
        return jsonify({"status": 404, "message": "Not found"}), 404
    return jsonify(task), 200

@app.route('/v1/tasks/<task_id>', methods=['PATCH'])
def patch_task(task_id):
    task = tasks_db.get(task_id)
    if not task:
        return jsonify({"status": 404, "message": "Not found"}), 404
    
    data = request.json or {}
    if 'title' in data:
        task['title'] = data['title']
    if 'status' in data:
        task['status'] = data['status']
    if 'priority' in data:
        task['priority'] = data['priority']
        
    return jsonify(task), 200

@app.route('/v1/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    if task_id in tasks_db:
        del tasks_db[task_id]
        return '', 204
    return jsonify({"status": 404, "message": "Not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)