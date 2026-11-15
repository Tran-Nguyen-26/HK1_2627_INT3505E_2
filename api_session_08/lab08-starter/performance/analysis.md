# Lab 4 — Phân tích kết quả

| Kịch bản | Users | Spawn rate | Duration | p95 (ms) | Failure rate | RPS |
|---|---:|---:|---:|---:|---:|---:|
| A | 10 | 2 | 30s | 18 | 0.00% | 4.63 |
| B | 50 | 5 | 60s | 28 | 0.36% | 23.40 |
| C | 200 | 50 | 30s | 110 | 0.24% | 97.62 |

1. **Kịch bản có p95 cao nhất là gì? Dùng số liệu quan sát để giải thích.**
   - Kịch bản C có p95 cao nhất (110 ms), tăng gấp ~6 lần kịch bản A (18 ms) và ~4 lần kịch bản B (28 ms).
   - Giải thích: Kịch bản C tạo tải đột biến (spike load) với 200 users được spawn với tốc độ 50 users/s trong chỉ 4 giây đầu. Số lượng request dồn dập khiến hàng đợi xử lý của Flask development server tăng nhanh (trung bình ~97.62 RPS), độ trễ hàng đợi tăng lên. Đặc biệt các tác vụ ghi CSDL như `POST /books` có p95 lên đến 160 ms do SQLite lock file khi ghi đồng thời, kéo theo toàn bộ độ trễ p95 chung tăng lên 110 ms.

2. **Endpoint nào tăng failure rate? Phân biệt lỗi HTTP thực và lỗi đánh dấu trong Locust.**
   - Endpoint phát sinh failure là `GET /books?year=` (chiếm tỷ lệ lỗi ~1.0% - 1.5% của riêng endpoint này: ở kịch bản B ghi nhận 5/333 failures ~ 1.50%, kịch bản C ghi nhận 7/696 failures ~ 1.01%).
   - Phân biệt:
     - Đây là **lỗi đánh dấu nhân tạo từ phía client của Locust** thông qua `response.failure(...)` khi hàm `search_by_year` cố ý tạo xác suất 1% giả lập lỗi 500.
     - Phía **server Flask thực tế không gặp lỗi hay crash 500 thực sự nào**; toàn bộ các request hợp lệ đều được trả về mã HTTP 200 từ server.

3. **Với SLO giả định p95 < 300 ms, kịch bản nào đạt? Nêu giới hạn của phép đo.**
   - Cả 3 kịch bản A, B, C đều đạt ngưỡng SLO giả định p95 < 300 ms (A đạt 18 ms, B đạt 28 ms, C đạt 110 ms).
   - Đề xuất baseline cho CI gate: Với bài test tải định kỳ 50 users (kịch bản B), có thể đặt ngưỡng cảnh báo SLO CI gate: `p95 < 60 ms` và `failure rate < 1%` (loại trừ các giả lập lỗi).
   - Giới hạn của phép đo:
     - Phép đo thực hiện hoàn toàn trên môi trường cục bộ (localhost), không mô phỏng độ trễ đường truyền Internet thực tế (RTT ~ 0ms).
     - Server là Werkzeug development server chạy đơn tiến trình cùng SQLite cục bộ, không đại diện cho kiến trúc production (WSGI multi-worker, pooling, CSDL độc lập như PostgreSQL).

4. **Nếu connection pool bị giới hạn ở 5, bạn sẽ kiểm chứng ảnh hưởng như thế nào?**
   - Hiện tượng: Khi 200 users gửi request đồng thời mà connection pool chỉ cho phép tối đa 5 kết nối CSDL, 195 users còn lại buộc phải đợi trong hàng đợi của pool. Khi hàng đợi quá tải hoặc vượt thời gian timeout (`QueuePool timeout`), server sẽ ném ngoại lệ `TimeoutError` và trả về mã lỗi 500. Độ trễ p95/p99 sẽ tăng vọt hoặc xuất hiện hàng loạt lỗi kết nối.
   - Cách kiểm chứng bằng Locust:
     - Cấu hình trong Flask app: `SQLALCHEMY_ENGINE_OPTIONS = {"pool_size": 5, "max_overflow": 0, "pool_timeout": 3}`.
     - Chạy lại kịch bản C (200 users, spawn rate 50/s) bằng Locust. Kết quả sẽ thấy cột `# fails` tăng vọt, phần Error report ghi nhận các lỗi HTTP 500 do CSDL cạn pool, và p95/max latency vọt lên mức trần timeout (> 3000 ms).
