from flask import Blueprint, Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, select, tuple_
import base64
import json

# Khởi tạo ứng dụng Flask và SQLAlchemy
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bookstore.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bp = Blueprint("books", __name__, url_prefix="/api/v1/books")

# --- 1. MODEL ĐỊNH NGHĨA DỮ LIỆU ---
class Book(db.Model):
    __tablename__ = "books"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(100), nullable=True)
    price_vnd = db.Column(db.Integer, nullable=False, default=0)
    stock = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            "id": f"book_{self.id}",
            "title": self.title,
            "genre": self.genre,
            "price_vnd": self.price_vnd,
            "stock": self.stock
        }

# --- 2. CÁC HÀM HELPER XỬ LÝ SORT & CURSOR ---
ALLOWED_SORT_COLUMNS = {
    "id": Book.id,
    "price": Book.price_vnd,
    "price_vnd": Book.price_vnd,
    "title": Book.title,
    "created_at": Book.created_at,
    "stock": Book.stock
}

DEFAULT_LIMIT = 20
MAX_LIMIT = 100

def parse_sort(raw_sort):
    if not raw_sort:
        raw_sort = "-id"
    
    cols = []
    sort_specs = []
    
    for s in raw_sort.split(","):
        s = s.strip()
        desc = s.startswith("-")
        key = s.lstrip("-")
        
        if key not in ALLOWED_SORT_COLUMNS:
            return None, None, f"Invalid sort key: {key}", 400
        
        col = ALLOWED_SORT_COLUMNS[key]
        cols.append(col.desc() if desc else col.asc())
        sort_specs.append({"key": key, "desc": desc})
    
    if "id" not in [spec["key"] for spec in sort_specs]:
        cols.append(Book.id.desc() if sort_specs[0]["desc"] else Book.id.asc())
        
    return cols, sort_specs, None, 200

def _encode_cursor(state):
    return base64.urlsafe_b64encode(json.dumps(state).encode()).decode().rstrip("=")

def _decode_cursor(raw_cursor):
    pad = "=" * (-len(raw_cursor) % 4)
    return json.loads(base64.urlsafe_b64decode(raw_cursor + pad))

def apply_cursor(q, raw_cursor, sort_specs, desc):
    if not raw_cursor:
        return q, None, 200
    try:
        c = _decode_cursor(raw_cursor)
    except Exception:
        return q, "invalid_cursor_format", 400
    
    if c.get("specs") != sort_specs:
        return q, "sort_criteria_changed", 400
    
    last_val, last_id = c["v"], c["i"]
    primary_col = ALLOWED_SORT_COLUMNS[sort_specs[0]["key"]]
    
    op = "<" if sort_specs[0]["desc"] else ">"
    condition = tuple_(primary_col, Book.id).op(op)((last_val, last_id))
    
    return q.filter(condition), None, 200

# --- 3. API ENDPOINT CHO SÁCH (LIST BOOKS) ---
@bp.get("")
def list_books():
    strategy = request.args.get("strategy", "cursor")
    limit = min(request.args.get("limit", DEFAULT_LIMIT, type=int), MAX_LIMIT)
    genre = request.args.get("genre")
    raw_sort = request.args.get("sort", "-id")
    
    cols, sort_specs, err, code = parse_sort(raw_sort)
    if err:
        return jsonify({"error": err}), code
        
    q = select(Book)
    if genre:
        q = q.filter(Book.genre == genre)
        
    q = q.order_by(*cols)
    
    if strategy == "offset":
        offset = request.args.get("offset", 0, type=int)
        
        count_q = select(func.count(Book.id))
        if genre:
            count_q = count_q.filter(Book.genre == genre)
        total = db.session.scalar(count_q)
        
        rows = db.session.scalars(q.offset(offset).limit(limit)).all()
        
        return jsonify({
            "data": [b.to_dict() for b in rows],
            "pagination": {
                "strategy": "offset",
                "offset": offset,
                "limit": limit,
                "total": total,
                "has_next": offset + limit < total
            }
        })
        
    else:
        raw_cursor = request.args.get("cursor")
        q, err, code = apply_cursor(q, raw_cursor, sort_specs, sort_specs[0]["desc"])
        if err:
            return jsonify({"error": err}), code
            
        rows = db.session.scalars(q.limit(limit + 1)).all()
        has_more = len(rows) > limit
        items = rows[:limit]
        
        next_cursor = None
        if items and has_more:
            last_item = items[-1]
            primary_key_name = sort_specs[0]["key"]
            last_val = getattr(last_item, ALLOWED_SORT_COLUMNS[primary_key_name].key)
            next_cursor = _encode_cursor({
                "specs": sort_specs,
                "v": last_val,
                "i": last_item.id
            })
            
        return jsonify({
            "data": [b.to_dict() for b in items],
            "pagination": {
                "strategy": "cursor",
                "next_cursor": next_cursor,
                "has_more": has_more
            }
        })

# Đăng ký Blueprint vào app
app.register_blueprint(bp)

@app.route("/")
def index():
    return {"message": "Bookstore API is running successfully!"}

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Tự động tạo bảng database
    app.run(debug=True, port=5000)