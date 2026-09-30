import json
import logging

from flask import Flask, request
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

PROBLEM_JSON = "application/problem+json"


class ProblemError(Exception):
    """Exception nghiệp vụ, sẽ được trả về dạng problem+json."""

    def __init__(self, status, title, detail=None,
                 type_="about:blank", **extra):
        super().__init__(title)
        self.status = status
        self.title = title
        self.detail = detail
        self.type = type_
        self.extra = extra


def problem_response(status, title, detail, type_="about:blank", extra=None):
    body = {
        "type": type_,
        "title": title,
        "status": status,
        "detail": detail,
        "instance": request.path,
    }
    body.update(extra or {})
    # Luôn trả problem+json, không phụ thuộc header Accept của client
    return app.response_class(json.dumps(body, ensure_ascii=False),
                              status=status, mimetype=PROBLEM_JSON)


@app.errorhandler(ProblemError)
def handle_problem(e):
    return problem_response(e.status, e.title, e.detail, e.type, e.extra)


@app.errorhandler(HTTPException)
def handle_http_exception(e):
    # 404, 405, 400... do Flask/Werkzeug tự ném
    return problem_response(e.code, e.name, e.description)


@app.errorhandler(Exception)
def handle_unexpected(e):
    # Chi tiết + stack trace chỉ ghi log server-side, không lộ ra client
    log.exception("Unhandled exception at %s %s", request.method, request.path)
    return problem_response(500, "Internal Server Error",
                            "Đã xảy ra lỗi phía máy chủ. Vui lòng thử lại sau.")


# ---- Route demo ----
resources = {1: {"id": 1, "name": "Demo"}}


@app.get("/resources/<int:id>")
def get_resource(id):
    item = resources.get(id)
    if item is None:
        raise ProblemError(
            404, "Resource Not Found",
            f"Không tìm thấy resource với id={id}",
            type_="https://example.com/problems/resource-not-found",
        )
    return item


@app.get("/boom")
def boom():
    raise RuntimeError("chi tiết nội bộ không được lộ ra")


if __name__ == "__main__":
    app.run(debug=False)