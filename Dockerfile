# Base image Python
FROM python:3.12-slim

# Cài các gói cần thiết để build mysqlclient và MySQL client
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    mysql-client \
    && rm -rf /var/lib/apt/lists/*

# Thư mục làm việc
WORKDIR /app

# Copy requirements và cài đặt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ project
COPY . .

# Biến môi trường Flask
ENV FLASK_APP=app/index.py
ENV FLASK_ENV=development
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Expose port
EXPOSE 5000

# Command để chạy app (dùng entrypoint)
ENTRYPOINT ["./entrypoint.sh"]
