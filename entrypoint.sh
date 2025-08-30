#!/bin/bash
set -e

# Biến môi trường MySQL
MYSQL_HOST=${MYSQL_HOST:-db}
MYSQL_USER=${MYSQL_USER:-user}
MYSQL_PASSWORD=${MYSQL_PASSWORD:-pass}
MYSQL_DATABASE=${MYSQL_DATABASE:-recruitmentdb}

echo "🟢 Chờ MySQL sẵn sàng..."
# Ping không cần cred; tránh lỗi auth không cần thiết khi chỉ kiểm tra aliveness
MAX_RETRIES=60
RETRY_COUNT=0
until mysqladmin ping -h"$MYSQL_HOST" --protocol=TCP --connect-timeout=5 --silent; do
  RETRY_COUNT=$((RETRY_COUNT+1))
  if [ "$RETRY_COUNT" -ge "$MAX_RETRIES" ]; then
    echo "❌ MySQL chưa sẵn sàng sau $MAX_RETRIES lần thử. Kiểm tra kết nối thủ công:"
    echo "   mysqladmin ping -h $MYSQL_HOST --protocol=TCP"
    echo "   mysql -h $MYSQL_HOST -u\"$MYSQL_USER\" -p\"$MYSQL_PASSWORD\" -e 'SELECT 1;'"
    exit 1
  fi
  echo "Chưa sẵn sàng, đợi 5s..."
  sleep 5
done
echo "✅ MySQL đã sẵn sàng!"

echo "⚡ Tạo bảng và chèn dữ liệu mẫu..."
python3 app/init_db.py

echo "🚀 Khởi động Flask server..."
FLASK_PORT=${FLASK_RUN_PORT:-5000}
flask run --host=0.0.0.0 --port=$FLASK_PORT