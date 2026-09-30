from flask import Flask, jsonify, request, url_for
from datetime import datetime, timezone

app = Flask(__name__)
API = "/api/v1"

posts = {}      # lưu tạm trong bộ nhớ
next_id = 1


def now():
    return datetime.now(timezone.utc).isoformat()


def error(status, message):
    return jsonify({"error": message}), status


@app.get(f"{API}/posts")
def list_posts():
    page = request.args.get("page", 1, type=int)
    size = request.args.get("size", 10, type=int)
    tag = request.args.get("tag")
    author = request.args.get("author", type=int)
    sort = request.args.get("sort", "-createdAt")

    items = list(posts.values())
    if tag:
        items = [p for p in items if tag in p["tags"]]
    if author:
        items = [p for p in items if p["authorId"] == author]

    field = sort.lstrip("-")
    if items and field not in items[0]:
        return error(400, f"Không thể sắp xếp theo '{field}'")
    items.sort(key=lambda p: p[field], reverse=sort.startswith("-"))

    total = len(items)
    start = (page - 1) * size
    return jsonify({
        "data": items[start:start + size],
        "page": page, "size": size, "total": total,
    })


@app.post(f"{API}/posts")
def create_post():
    global next_id
    body = request.get_json(silent=True) or {}
    if not body.get("title") or not body.get("content"):
        return error(400, "title và content là bắt buộc")

    post = {
        "id": next_id,
        "title": body["title"],
        "content": body["content"],
        "authorId": body.get("authorId"),
        "tags": body.get("tags", []),
        "createdAt": now(),
        "updatedAt": now(),
    }
    posts[next_id] = post
    next_id += 1

    resp = jsonify(post)
    resp.status_code = 201
    resp.headers["Location"] = url_for("get_post", post_id=post["id"])
    return resp


@app.get(f"{API}/posts/<int:post_id>")
def get_post(post_id):
    post = posts.get(post_id)
    return jsonify(post) if post else error(404, "Không tìm thấy bài viết")


@app.put(f"{API}/posts/<int:post_id>")
def replace_post(post_id):
    post = posts.get(post_id)
    if not post:
        return error(404, "Không tìm thấy bài viết")
    body = request.get_json(silent=True) or {}
    if not body.get("title") or not body.get("content"):
        return error(400, "PUT cần đủ title và content")
    post.update(title=body["title"], content=body["content"],
                tags=body.get("tags", []), updatedAt=now())
    return jsonify(post)


@app.patch(f"{API}/posts/<int:post_id>")
def update_post(post_id):
    post = posts.get(post_id)
    if not post:
        return error(404, "Không tìm thấy bài viết")
    body = request.get_json(silent=True) or {}
    for key in ("title", "content", "tags"):
        if key in body:
            post[key] = body[key]
    post["updatedAt"] = now()
    return jsonify(post)


@app.delete(f"{API}/posts/<int:post_id>")
def delete_post(post_id):
    if posts.pop(post_id, None) is None:
        return error(404, "Không tìm thấy bài viết")
    return "", 204


if __name__ == "__main__":
    app.run(debug=True)