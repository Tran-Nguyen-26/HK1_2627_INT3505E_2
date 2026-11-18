from datetime import datetime, timezone
from flask import Blueprint
from .users_data import get_user
from sunset import add_sunset_headers

bp = Blueprint("v1", __name__)
V1_SUNSET = datetime(2027, 6, 30, 23, 59, 59, tzinfo=timezone.utc)


@bp.route("/users/<int:uid>")
def get(uid):
    u = get_user(uid)
    if not u:
        return {"error": "not found"}, 404
    return {"id": uid,
            "full_name": f"{u['first_name']} {u['last_name']}",
            "email": u["email"]}


@bp.after_request
def deprecate(resp):
    return add_sunset_headers(resp, V1_SUNSET, "/api/v2/users")
