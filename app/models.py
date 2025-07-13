from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship, backref
from app import db, app
from datetime import datetime
from enum import Enum
from flask_login import UserMixin

# ========== ENUM KHAI BÁO ==========
class RoleEnum(Enum):
    ADMIN = "Admin"
    JOBSEEKER = "JobSeeker"
    RECRUITER = "Recruiter"

class JobStatusEnum(Enum):
    DRAFT = "Draft"
    ACTIVE = "Active"
    CLOSED = "Closed"
    EXPIRED = "Expired"

class ApplicationStatusEnum(Enum):
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    INTERVIEW = "Interview"
    REJECTED = "Rejected"
    ACCEPTED = "Accepted"

class InterviewStatusEnum(Enum):
    SCHEDULED = "Scheduled"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

# ========== BASE MODEL ==========
class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id}>"

# ========== MIDDLE TABLE ==========
conversation_user = db.Table(
    'conversation_user',
    db.Column('user_id', Integer, ForeignKey('user.id')),
    db.Column('conversation_id', db.Integer, db.ForeignKey('conversation.id'))
)

# ========== USER & RELATED ==========
class User(BaseModel, UserMixin):
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(20), default=RoleEnum.JOBSEEKER.value)
    avatar = db.Column(db.String(255))
    joined_date = db.Column(db.DateTime, default=datetime.utcnow)
    phone = db.Column(db.String(20))
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    conversation = relationship("Conversation", secondary=conversation_user, backref=backref('users', lazy=True))

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}" if self.first_name or self.last_name else self.username

    def is_admin(self):
        return self.role == RoleEnum.ADMIN.value

    def is_job_seeker(self):
        return self.role == RoleEnum.JOBSEEKER.value

    def is_recruiter(self):
        return self.role == RoleEnum.RECRUITER.value

    def get_avatar_url(self):
        return self.avatar if self.avatar else "https://www.gravatar.com/avatar/"

    def __str__(self):
        return self.get_full_name()

class JobSeeker(BaseModel):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    skill = db.Column(db.String(255))
    experience = db.Column(db.String(255))
    education = db.Column(db.String(255))
    preferred_locations = db.Column(db.String(255))
    preferred_job_types = db.Column(db.String(255))
    linkedin_url = db.Column(db.String(255))

    user = relationship("User", backref=backref("job_seeker", uselist=False))

class Recruiter(BaseModel):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    website = db.Column(db.String(255))
    introduction = db.Column(db.Text)
    company_name = db.Column(db.String(255))
    industry = db.Column(db.String(100))
    company_size = db.Column(db.String(50))
    verification_status = db.Column(db.String(50))
    location = db.Column(db.String(100))

    user = relationship("User", backref=backref("recruiter", uselist=False))

# ========== JOB & APPLICATION ==========
class Category(BaseModel):
    name = Column(String(50), nullable=False)
    description = Column(String(255), nullable=True)
    jobPostings = relationship("JobPosting", backref="category", lazy=True)

    def __str__(self):
        return self.name



class JobPosting(BaseModel):
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)
    location = db.Column(db.String(100))
    salary = db.Column(db.Integer)
    employment_type = db.Column(db.String(50))
    status = db.Column(db.String(20), default=JobStatusEnum.DRAFT.value)
    expiration_date = db.Column(db.DateTime)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime)
    view_count = db.Column(db.Integer, default=0)
    recruiter_id = db.Column(db.Integer, db.ForeignKey('recruiter.id'))
    category_id = Column(Integer, ForeignKey("category.id"))

    recruiter = relationship('Recruiter', backref='job_postings', lazy=True)

    tags = relationship("Tag", secondary="tag_jobposting", lazy="subquery", backref=backref("jobposting",lazy=True))

    def __str__(self):
        return self.title


tag_jobposting = db.Table(
    'tag_jobposting',
    Column('jobposting_id',Integer, ForeignKey('job_posting.id') ,primary_key=True),
    Column('tag_id', Integer, ForeignKey('tag.id'), primary_key=True)
)

class Tag(BaseModel):
    name = Column(String(255), nullable=False)



class Resume(BaseModel):
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    created_date = db.Column(db.DateTime, default=datetime.now())
    updated_date = db.Column(db.DateTime)
    job_seeker_id = db.Column(db.Integer, db.ForeignKey('job_seeker.id'))

    job_seeker = relationship("JobSeeker", backref="resumes")

class Application(BaseModel):
    cover_letter = db.Column(db.Text)
    status = db.Column(db.String(20), default=ApplicationStatusEnum.DRAFT.value)
    applied_date = db.Column(db.DateTime, default=datetime.now())
    updated_date = db.Column(db.DateTime)
    feedback = db.Column(db.Text)
    resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'))
    job_posting_id = db.Column(db.Integer, db.ForeignKey('job_posting.id'))

    resume = relationship("Resume")
    job_posting = relationship("JobPosting")

class Interview(BaseModel):
    dateTime = db.Column(db.DateTime)
    status = db.Column(db.String(20), default=InterviewStatusEnum.SCHEDULED.value)
    url = db.Column(db.String(255))
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'))

    application = relationship("Application", backref="interviews", lazy=True)

# ========== CHAT ==========
class Conversation(BaseModel):
    created_date = db.Column(db.DateTime, default=datetime.now())

class Chat(BaseModel):
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.now())
    is_read = db.Column(db.Boolean, default=False)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    conversation = relationship("Conversation", backref="chats", lazy=True)
    sender = relationship("User")

# ========== NOTIFICATION ==========
class Notification(BaseModel):
    content = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    created_date = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    user = relationship("User", backref="notifications")

class NotificationChannel(BaseModel):
    channel_type = db.Column(db.String(50))
    status = db.Column(db.String(50))
    sent_at = db.Column(db.DateTime)
    notification_id = db.Column(db.Integer, db.ForeignKey('notification.id'))

    notification = relationship("Notification", backref="channels")


if __name__ == '__main__':
    with app.app_context():
        db.drop_all()  # Use with caution, this will delete all data
        db.create_all()
