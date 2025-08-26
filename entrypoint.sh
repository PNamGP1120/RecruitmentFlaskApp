#!/bin/bash
set -e

echo "Waiting for MySQL to start..."
until python - <<EOF
import pymysql
try:
    pymysql.connect(
        host="$MYSQL_HOST",
        user="$MYSQL_USER",
        password="$MYSQL_PASSWORD",
        database="$MYSQL_DATABASE"
    )
except Exception:
    import sys, time
    time.sleep(1)
    sys.exit(1)
EOF
do
    echo "MySQL is unavailable - sleeping"
done

# Chạy script init_db.py để tạo các bảng (nếu bạn muốn tự động)
echo "Creating tables..."
python -m app.init_db

# Khởi động Flask
echo "Starting Flask app..."
exec python -m app.run
