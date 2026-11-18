from flask import Blueprint, request
from .users_data import get_user, create_user

bp = Blueprint("v2", __name__)


@bp.route("/users/<int:uid>")
def get(uid):
    u = get_user(uid)
    if not u:
        return {"error": "not found"}, 404
    return {"id": uid,
            "first_name": u["first_name"],
            "last_name": u["last_name"],
            "email": u["email"]}


@bp.route("/users", methods=["POST"])
def create():
    body = request.get_json(silent=True) or {}
    missing = [k for k in ("first_name", "last_name", "email") if not body.get(k)]
    if missing:
        return {"error": "missing fields", "fields": missing}, 400
    uid = create_user(body["first_name"], body["last_name"], body["email"])
    return {"id": uid, **{k: body[k] for k in ("first_name", "last_name", "email")}}, 201
