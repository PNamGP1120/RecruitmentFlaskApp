from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import Select2Field
from app import app, db
from app.models import (
    User, JobSeeker, Recruiter, Resume, JobPosting,
    Application, Interview, Conversation, Chat,
    Notification, NotificationChannel
)

# ===== Custom View để xử lý Enum dưới dạng String =====
class UserAdminView(ModelView):
    form_overrides = {
        'role': Select2Field
    }
    form_args = {
        'role': {
            'choices': [
                ('Admin', 'Admin'),
                ('JobSeeker', 'JobSeeker'),
                ('Recruiter', 'Recruiter')
            ]
        }
    }
    column_exclude_list = ['password']

class JobPostingAdminView(ModelView):
    form_overrides = {
        'status': Select2Field
    }
    form_args = {
        'status': {
            'choices': [
                ('Draft', 'Draft'),
                ('Active', 'Active'),
                ('Closed', 'Closed'),
                ('Expired', 'Expired')
            ]
        }
    }

class ApplicationAdminView(ModelView):
    form_overrides = {
        'status': Select2Field
    }
    form_args = {
        'status': {
            'choices': [
                ('Draft', 'Draft'),
                ('Submitted', 'Submitted'),
                ('Interview', 'Interview'),
                ('Rejected', 'Rejected'),
                ('Accepted', 'Accepted')
            ]
        }
    }

class InterviewAdminView(ModelView):
    form_overrides = {
        'status': Select2Field
    }
    form_args = {
        'status': {
            'choices': [
                ('Scheduled', 'Scheduled'),
                ('Completed', 'Completed'),
                ('Cancelled', 'Cancelled')
            ]
        }
    }

# ===== Khởi tạo Flask-Admin =====
admin = Admin(app, template_mode='bootstrap4', name='Recruitment Admin')

# ===== Thêm các model vào Admin =====
admin.add_view(UserAdminView(User, db.session))
admin.add_view(ModelView(JobSeeker, db.session))
admin.add_view(ModelView(Recruiter, db.session))
admin.add_view(ModelView(Resume, db.session))
admin.add_view(JobPostingAdminView(JobPosting, db.session))
admin.add_view(ApplicationAdminView(Application, db.session))
admin.add_view(InterviewAdminView(Interview, db.session))
admin.add_view(ModelView(Conversation, db.session))
admin.add_view(ModelView(Chat, db.session))
admin.add_view(ModelView(Notification, db.session))
admin.add_view(ModelView(NotificationChannel, db.session))
