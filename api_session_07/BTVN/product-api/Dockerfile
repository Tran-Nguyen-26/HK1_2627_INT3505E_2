# Stage 1: Builder
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim
WORKDIR /app

# Tạo non-root user 'app'
RUN groupadd -r app && useradd -r -g app -d /app app

# Copy Python packages từ stage builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy toàn bộ mã nguồn ứng dụng
COPY . .

# Phân quyền thư mục cho user app
RUN chown -R app:app /app
USER app

EXPOSE 5000

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=wsgi.py

# Tự động thực thi migration DB trước khi khởi chạy Gunicorn WSGI Server
CMD ["sh", "-c", "flask db upgrade && gunicorn --bind 0.0.0.0:5000 --workers 2 wsgi:app"]
