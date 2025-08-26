#!/bin/bash
set -e

# Chờ database sẵn sàng
echo "Waiting for MySQL..."
while ! mysqladmin ping -h"$MYSQL_HOST" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" --silent; do
    sleep 1
done
echo "MySQL is ready!"

# Tạo bảng nếu chưa có
python -m app.init_db

# Thêm data mặc định nếu cần
python run.py

# Chạy Flask app
python index.py
