import pytest
from jsonschema import validate, ValidationError

def test_get_books_empty(client):
    """A. GET /books khi CSDL rỗng trả về mảng rỗng []"""
    response = client.get('/books')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 0

def test_get_book_not_found(client):
    """B. GET /books/<id> với id không tồn tại trả về 400/404 + JSON chứa thông tin lỗi"""
    response = client.get('/books/non_existent_id_999')
    assert response.status_code in [400, 404]
    data = response.get_json()
    assert data is not None

def test_post_books_missing_title(client):
    """C. POST /books thiếu title trả về 400 + trong errors có field 'title'"""
    response = client.post('/books', json={"author": "Test Author"})
    assert response.status_code == 400
    data = response.get_json()
    assert 'errors' in data
    
    errors = data['errors']
    if isinstance(errors, list):
        fields = [err.get('field') for err in errors]
        assert 'title' in fields
    else:
        assert 'title' in errors

def test_delete_then_get(client):
    """D. Xoá rồi GET cùng id — phải trả về lỗi không tìm thấy (400/404)"""
    create_res = client.post('/books', json={"title": "Book to Delete", "author": "Author"})
    book = create_res.get_json()
    book_id = book.get('id') or book.get('data', {}).get('id')

    delete_res = client.delete(f'/books/{book_id}')
    assert delete_res.status_code in [200, 204]

    get_res = client.get(f'/books/{book_id}')
    assert get_res.status_code in [400, 404]

def test_response_extra_field_blocked(client):
    """Bước 2, Bonus: Dùng jsonschema chứng minh backend không lộ password_hash hoặc field lạ"""
    create_res = client.post('/books', json={"title": "Secure Book", "author": "Author"})
    book = create_res.get_json()
    book_id = book.get('id') or book.get('data', {}).get('id')

    response = client.get(f'/books/{book_id}')
    assert response.status_code == 200
    data = response.get_json()

    # Chứng minh tường minh rằng không lộ password_hash trong response
    assert "password_hash" not in data, "Phát hiện lộ password_hash trong response!"

    # Định nghĩa schema chặn các trường ngoài lề không cho phép (additionalProperties: False)
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": ["string", "integer"]},
            "title": {"type": "string"},
            "author": {"type": ["string", "null"]},
            "isbn": {"type": ["string", "null"]},
            "year": {"type": ["integer", "null"]}
        },
        "required": ["id", "title"],
        "additionalProperties": False
    }

    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        pytest.fail(f"Phát hiện trường dữ liệu lạ bị lộ hoặc vi phạm schema: {e}")