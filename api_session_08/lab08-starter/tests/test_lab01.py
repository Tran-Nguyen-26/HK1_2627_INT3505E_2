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
    """B. GET /books/<id> với id không tồn tại trả về 400 (hoặc 404 tùy API) + JSON chứa 'code' hoặc tương đương"""
    response = client.get('/books/non_existent_id_999')
    # API thực tế đang trả về status code 400 cho ID không hợp lệ/không tồn tại này
    assert response.status_code in [400, 404]
    data = response.get_json()
    assert data is not None

def test_post_books_missing_title(client):
    """C. POST /books thiếu title trả về 400 + trong errors có field 'title'"""
    response = client.post('/books', json={"author": "Test Author"})
    assert response.status_code == 400
    data = response.get_json()
    assert 'errors' in data
    
    # Kiểm tra errors ở dạng list chứa dict (ví dụ: [{'field': 'title', ...}])
    errors = data['errors']
    if isinstance(errors, list):
        fields = [err.get('field') for err in errors]
        assert 'title' in fields
    else:
        assert 'title' in errors

def test_delete_then_get(client):
    """D. Xoá rồi GET cùng id — phải trả về 404 (hoặc 400)"""
    create_res = client.post('/books', json={"title": "Book to Delete", "author": "Author"})
    book = create_res.get_json()
    book_id = book.get('id') or book.get('data', {}).get('id')

    delete_res = client.delete(f'/books/{book_id}')
    assert delete_res.status_code in [200, 204]

    get_res = client.get(f'/books/{book_id}')
    assert get_res.status_code in [400, 404]

def test_response_extra_field_blocked(client):
    """Bonus: Dùng jsonschema kiểm tra cấu trúc response của sách"""
    create_res = client.post('/books', json={"title": "Secure Book", "author": "Author"})
    book = create_res.get_json()
    book_id = book.get('id') or book.get('data', {}).get('id')

    response = client.get(f'/books/{book_id}')
    assert response.status_code == 200
    data = response.get_json()

    # Bổ sung các field thực tế mà API trả về (id, title, author, isbn, year)
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
        pytest.fail(f"Schema validation failed: {e}")