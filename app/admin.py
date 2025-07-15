from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from app import app, db
from app.models import (
    User, Company, Category, Job, CV, Application, Interview, Conversation, Message, Notification,
)

class CategoryView(ModelView):
    column_list = ['name', 'jobs']

# ===== Khởi tạo Flask-Admin =====
admin = Admin(app, template_mode='bootstrap4', name='Recruitment Admin')

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Company, db.session))
admin.add_view(CategoryView(Category, db.session))
admin.add_view(ModelView(Job, db.session))
admin.add_view(ModelView(CV, db.session))
admin.add_view(ModelView(Application, db.session))
admin.add_view(ModelView(Interview, db.session))
admin.add_view(ModelView(Conversation, db.session))
admin.add_view(ModelView(Message, db.session))
admin.add_view(ModelView(Notification, db.session))

