# app/init_db.py
from app import db, app
from app.run import populate_sample_data
with app.app_context():
    # Tạo tất cả bảng trong DB
    db.drop_all()
    db.create_all()
    populate_sample_data()
    print("All tables created!")
