FROM python:3.11-slim

# Cập nhật và cài dependency cần thiết cho mysqlclient
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    libssl-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Tạo thư mục app
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Upgrade pip và cài các package python
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ project
COPY . .

# Expose port
EXPOSE 5000

# Entry point
CMD ["python", "run.py"]
