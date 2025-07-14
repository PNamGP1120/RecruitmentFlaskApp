from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from app import app, db
from app.models import (
    User
)

class CategoryView(ModelView):
    column_list = ['name', 'jobs']

# ===== Khởi tạo Flask-Admin =====
admin = Admin(app, template_mode='bootstrap4', name='Recruitment Admin')

admin.add_view(ModelView(User, db.session))
