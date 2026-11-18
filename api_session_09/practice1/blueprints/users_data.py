USERS = {
    1: {"first_name": "Văn", "last_name": "Nguyễn", "email": "a@vnu.vn"},
    2: {"first_name": "Trang", "last_name": "Trần", "email": "b@vnu.vn"},
}
_next_id = 3


def get_user(uid):
    return USERS.get(uid)


def create_user(first_name, last_name, email):
    global _next_id
    uid = _next_id
    _next_id += 1
    USERS[uid] = {"first_name": first_name, "last_name": last_name, "email": email}
    return uid
