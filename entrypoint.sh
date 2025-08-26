#!/bin/bash
set -e

# Đợi MySQL sẵn sàng
echo "Waiting for MySQL to start..."
while ! mysqladmin ping -h"$MYSQL_HOST" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" --silent; do
    sleep 1
done

echo "MySQL started!"

# Nếu muốn tạo database mặc định
echo "Ensuring database exists..."
mysql -h"$MYSQL_HOST" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS \`$MYSQL_DATABASE\`;"

# Chạy script init_db.py để tạo các bảng (nếu bạn muốn tự động)
echo "Creating tables..."
python -m app.init_db

# Khởi động Flask
echo "Starting Flask app..."
exec python -m app.run
