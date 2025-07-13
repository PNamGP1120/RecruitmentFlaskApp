from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import Select2Field
from app import app, db
from app.models import (
    User, JobSeeker, Recruiter, Resume, JobPosting,
    Application, Interview, Conversation, Chat,
    Notification, NotificationChannel, Category
)


# ===== Khởi tạo Flask-Admin =====
admin = Admin(app, template_mode='bootstrap4', name='Recruitment Admin')

class CategoryView(ModelView):
    column_list = ['name', 'jobs']


class JobPostingView(ModelView):
    column_list = ['id', 'description']

# ===== Thêm các model vào Admin =====
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(JobSeeker, db.session))
admin.add_view(ModelView(Recruiter, db.session))
admin.add_view(ModelView(Resume, db.session))
admin.add_view(ModelView(JobPosting, db.session))
admin.add_view(ModelView(Application, db.session))
admin.add_view(ModelView(Interview, db.session))
admin.add_view(ModelView(Conversation, db.session))
admin.add_view(ModelView(Chat, db.session))
admin.add_view(ModelView(Notification, db.session))
admin.add_view(ModelView(NotificationChannel, db.session))
admin.add_view(CategoryView(Category, db.session))
