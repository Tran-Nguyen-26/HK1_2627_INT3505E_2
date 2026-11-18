import logging
from datetime import datetime, timezone

from flask import Flask

from sunset import deprecate_at

logging.basicConfig(level=logging.WARNING)
app = Flask(__name__)
app.json.ensure_ascii = False

V1_SUNSET = datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc)   # chưa tới -> 200
OLD_SUNSET = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)       # đã qua -> 410


@app.route("/api/v1/users/<int:uid>")
@deprecate_at(V1_SUNSET, replacement="/api/v2/users")
def get_v1(uid):
    return {"id": uid, "full_name": "Nguyễn Văn A"}


# Endpoint đã qua sunset, để test 410 Gone
@app.route("/api/v0/users/<int:uid>")
@deprecate_at(OLD_SUNSET, replacement="/api/v2/users")
def get_v0(uid):
    return {"id": uid, "name": "legacy"}


@app.route("/api/v2/users/<int:uid>")
def get_v2(uid):
    return {"id": uid, "first_name": "Văn", "last_name": "Nguyễn"}


if __name__ == "__main__":
    app.run(port=5002, debug=True)
