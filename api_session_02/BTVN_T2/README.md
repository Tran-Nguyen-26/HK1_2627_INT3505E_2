# BÀI TẬP 2: AUDIT MỘT PUBLIC API THỰC

* **Public API được chọn:** GitHub REST API (v3)
* **Trang tài liệu gốc:** [GitHub REST API Documentation](https://docs.github.com/en/rest)

---

## 1. Lấy thông tin công khai của người dùng (Get User Profile)

* **Endpoint:** `GET https://api.github.com/users/{username}`
* **Method:** `GET`
* **Status Code:**
  * `200 OK`: Trả về dữ liệu chi tiết của người dùng thành công.
  * `404 Not Found`: Không tìm thấy `username` tương ứng.
* **Headers quan trọng:**
  * **Request:** `Accept: application/vnd.github.v3+json`
  * **Response:** `Content-Type: application/json; charset=utf-8`, `X-RateLimit-Limit`, `X-RateLimit-Remaining`
* **Đánh giá RESTful:** **CÓ**
  * Sử dụng đúng phương thức `GET` để truy xuất dữ liệu mà không làm thay đổi tài nguyên trên server.
  * Đường dẫn dùng danh từ (`/users`) kết hợp định danh tài nguyên (`/{username}`) rõ ràng.

---

## 2. Tạo một Repository mới (Create Repository)

* **Endpoint:** `POST https://api.github.com/user/repos`
* **Method:** `POST`
* **Status Code:**
  * `201 Created`: Tạo repository thành công.
  * `401 Unauthorized`: Chưa xác thực hoặc Access Token không hợp lệ.
  * `422 Unprocessable Entity`: Dữ liệu gửi lên bị lỗi validation (ví dụ: thiếu tên kho lưu trữ, tên bị trùng).
* **Headers quan trọng:**
  * **Request:** `Authorization: Bearer <YOUR_ACCESS_TOKEN>`, `Content-Type: application/json`
  * **Response:** `Location: https://api.github.com/repos/{owner}/{repo}` (chỉ tới tài nguyên vừa tạo)
* **Đánh giá RESTful:** **CÓ**
  * Sử dụng method `POST` đúng mục đích tạo mới tài nguyên.
  * Response mã `201 Created` kèm theo header `Location` trỏ đến đường dẫn của tài nguyên vừa tạo là chuẩn mực thiết kế REST.

---

## 3. Cập nhật thông tin Repository (Update Repository)

* **Endpoint:** `PATCH https://api.github.com/repos/{owner}/{repo}`
* **Method:** `PATCH`
* **Status Code:**
  * `200 OK`: Cập nhật thông tin kho lưu trữ thành công.
  * `403 Forbidden`: Tài khoản không đủ quyền chỉnh sửa kho lưu trữ này.
  * `404 Not Found`: Kho lưu trữ không tồn tại.
* **Headers quan trọng:**
  * **Request:** `Authorization: Bearer <YOUR_ACCESS_TOKEN>`, `Content-Type: application/json`
* **Đánh giá RESTful:** **CÓ**
  * Đã áp dụng `PATCH` để cập nhật từng phần (partial update) thay vì `PUT` (thay thế toàn bộ tài nguyên), giúp giảm lưu lượng truyền tải và tối ưu hơn.

---

## 4. Xóa một Repository (Delete Repository)

* **Endpoint:** `DELETE https://api.github.com/repos/{owner}/{repo}`
* **Method:** `DELETE`
* **Status Code:**
  * `204 No Content`: Xóa thành công và không trả về dữ liệu nào trong phần Body.
  * `403 Forbidden`: Không có quyền xóa kho lưu trữ này.
  * `404 Not Found`: Kho lưu trữ không tồn tại hoặc đã bị xóa trước đó.
* **Headers quan trọng:**
  * **Request:** `Authorization: Bearer <YOUR_ACCESS_TOKEN>`
* **Đánh giá RESTful:** **CÓ**
  * Sử dụng chuẩn ngữ nghĩa của phương thức `DELETE`.
  * Trả về đúng status code `204 No Content` cho thao tác xóa thành công không cần dữ liệu phản hồi.

---

## 5. Lấy danh sách Issue trong một Repository (List Repository Issues)

* **Endpoint:** `GET https://api.github.com/repos/{owner}/{repo}/issues`
* **Method:** `GET`
* **Status Code:**
  * `200 OK`: Lấy danh sách các issue thành công.
  * `301 Moved Permanently`: Repository đã được đổi tên hoặc chuyển sang vị trí khác.
* **Headers quan trọng:**
  * **Request:** `Accept: application/vnd.github.v3+json`
  * **Response:** `Link` (Dùng cho việc phân trang RESTful API: `rel="next"`, `rel="last"`, v.v.)
* **Đánh giá RESTful:** **CÓ**
  * Thể hiện mối quan hệ cha - con (Sub-resources) rất rõ ràng trong kiến trúc URI: các `issues` nằm bên trong một `repo` cụ thể của `owner`.
  * Hỗ trợ HATEOAS thông qua header `Link` cho việc chuyển trang (Pagination).

---

## TỔNG KẾT

GitHub REST API là một trong những ví dụ mẫu mực về kiến trúc **RESTful API**:
- Định tuyến dựa trên tài nguyên (Resource-based routing).
- Sử dụng đúng ngữ nghĩa các phương thức HTTP Verbs (`GET`, `POST`, `PATCH`, `DELETE`).
- Sử dụng chính xác các mã trạng thái HTTP Status Code.
- Đầy đủ thông tin định danh và phân trang thông qua HTTP Headers.