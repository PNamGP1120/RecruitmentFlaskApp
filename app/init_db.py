# app/init_db.py
from app import db
from app.models import *
with app.app_context():
    # Tạo tất cả bảng trong DB
    db.create_all()
    print("All tables created!")
