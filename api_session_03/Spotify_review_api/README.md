# Báo cáo Review API: Spotify Web API
**API được chọn:** [Spotify Web API Documentation](https://developer.spotify.com/documentation/web-api)  
**Phân công thực hiện:** Tiêu chí 03 & Tiêu chí 04

---

## Tiêu chí 03: Idempotency rõ ràng (Idempotency)
> *Yêu cầu checklist: POST cần Idempotency-Key. PUT/DELETE idempotent. Tài liệu hoá rõ.*

### 1. Đánh giá phương thức PUT & DELETE (Đạt chuẩn Idempotency)
* Các request dùng method **PUT** (ví dụ: `PUT /v1/playlists/{playlist_id}` dùng để cập nhật thông tin chi tiết của playlist) và **DELETE** (ví dụ: `DELETE /v1/playlists/{playlist_id}/tracks` dùng để xóa bài hát khỏi playlist) của Spotify đều có tính chất **idempotent**.
* **Đặc điểm:** Việc thực hiện một request PUT hoặc DELETE nhiều lần liên tiếp với cùng một tham số sẽ mang lại trạng thái hệ thống không đổi sau lần gọi đầu tiên, không gây ra side-effect hay lỗi dữ liệu ngoài ý muốn.

### 2. Đánh giá phương thức POST (Cần cải thiện)
* Các thao tác **POST** trong hệ thống (chẳng hạn như `POST /v1/playlists/{playlist_id}/tracks` để thêm bài hát vào danh sách phát) hiện tại **không** bắt buộc hay tài liệu hóa việc sử dụng header `Idempotency-Key`.
* **Rủi ro:** Khi xảy ra sự cố mạng (timeout, rớt mạng), client thực hiện retry request POST, hệ thống Spotify có thể sẽ tiến hành thêm trùng lặp bài hát vào playlist mà không có cơ chế tự động chặn (deduplication) ở tầng gateway.
* **Đề xuất cải thiện:** Spotify nên bổ sung cơ chế truyền `Idempotency-Key` trên header cho các request POST làm thay đổi trạng thái dữ liệu quan trọng nhằm đảm bảo an toàn tuyệt đối khi mạng không ổn định.

---

## Tiêu chí 04: Error response có cấu trúc
> *Yêu cầu checklist: RFC 7807 problem+json nhất quán. Có type, title, detail, instance.*

### 1. Thực trạng cấu trúc lỗi của Spotify Web API (Không đạt chuẩn RFC 7807)
Khi hệ thống xảy ra lỗi (ví dụ lỗi xác thực token hết hạn), Spotify trả về cấu trúc JSON dạng custom bọc bên trong một object `error` như sau:

```json
{
  "error": {
    "status": 401,
    "message": "The access token expired"
  }
}