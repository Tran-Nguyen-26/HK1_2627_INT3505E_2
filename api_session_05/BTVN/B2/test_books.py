import pytest
from app import app, db, Book

@pytest.fixture
def client():
    # Cấu hình ứng dụng chạy ở chế độ testing và dùng database SQLite tạm thời trong RAM
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            
            # Thêm dữ liệu mẫu vào DB để test
            sample_books = [
                Book(title="Clean Code", genre="tech", price_vnd=450000, stock=10),
                Book(title="The Pragmatic Programmer", genre="tech", price_vnd=500000, stock=5),
                Book(title="Atomic Habits", genre="self-help", price_vnd=250000, stock=20),
                Book(title="Deep Work", genre="self-help", price_vnd=300000, stock=15),
            ]
            db.session.add_all(sample_books)
            db.session.commit()
            
            yield client
            
            db.drop_all()

def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.get_json()["message"] == "Bookstore API is running successfully!"

def test_list_books_offset_strategy(client):
    # Test phân trang theo offset, có lọc theo genre và sort
    response = client.get("/api/v1/books?strategy=offset&genre=tech&sort=-price,title&limit=1&offset=0")
    assert response.status_code == 200
    data = response.get_json()
    
    assert "data" in data
    assert len(data["data"]) == 1
    assert data["pagination"]["strategy"] == "offset"
    assert data["pagination"]["total"] == 2
    assert data["pagination"]["has_next"] is True

def test_list_books_cursor_strategy(client):
    # Test phân trang theo cursor (mặc định)
    response = client.get("/api/v1/books?strategy=cursor&limit=2")
    assert response.status_code == 200
    data = response.get_json()
    
    assert "data" in data
    assert len(data["data"]) == 2
    assert data["pagination"]["strategy"] == "cursor"
    assert "next_cursor" in data["pagination"]

def test_invalid_sort_key(client):
    # Test truyền tham số sort không hợp lệ phải trả về lỗi 400
    response = client.get("/api/v1/books?sort=invalid_column_name")
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data