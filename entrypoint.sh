#!/bin/bash
set -e

echo "🟢 Chờ MySQL sẵn sàng..."
# Lặp kiểm tra MySQL
until mysql -h"$MYSQL_HOST" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" &> /dev/null
do
  echo "Chưa sẵn sàng, đợi 5s..."
  sleep 5
done
echo "✅ MySQL đã sẵn sàng!"

# Khởi tạo database và populate dữ liệu
echo "⚡ Tạo bảng và chèn dữ liệu mẫu..."
python3 -m app.init_db

# Chạy Flask
echo "🚀 Khởi động Flask server..."
flask run --host=0.0.0.0 --port=5000
