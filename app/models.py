from sqlalchemy import Column, Integer, ForeignKey, String, Enum, DateTime, Boolean, Text
from sqlalchemy.orm import relationship, backref
from app import db, app
from datetime import datetime
from enum import Enum as MyEnum
from flask_login import UserMixin

# ========== ENUM KHAI BÁO ==========
class RoleEnum(MyEnum):
    ADMIN = "Admin"
    JOBSEEKER = "JobSeeker"
    RECRUITER = "Recruiter"

class JobStatusEnum(MyEnum):
    DRAFT = "Draft"
    ACTIVE = "Active"
    CLOSED = "Closed"
    EXPIRED = "Expired"

class ApplicationStatusEnum(MyEnum):
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    INTERVIEW = "Interview"
    REJECTED = "Rejected"
    ACCEPTED = "Accepted"

class InterviewStatusEnum(MyEnum):
    SCHEDULED = "Scheduled"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

# ========== BASE MODEL ==========
class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id}>"

# ========== MIDDLE TABLE ==========
conversation_user = db.Table(
    'conversation_user',
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('conversation_id', Integer, ForeignKey('conversation.id'))
)

# ========== USER & RELATED ==========
class User(BaseModel, UserMixin):
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100), unique=True, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.JOBSEEKER.value)
    avatar = Column(String(255))
    joined_date = Column(DateTime, default=datetime.now())
    phone = Column(String(20))
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)

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


class JobSeeker(User):
    skill = Column(String(255))
    experience = Column(String(255))
    education = Column(String(255))
    preferred_locations = Column(String(255))
    preferred_job_types = Column(String(255))
    linkedin_url = Column(String(255))


class Recruiter(User):
    website = Column(String(255))
    introduction = Column(Text)
    company_name = Column(String(255))
    industry = Column(String(100))
    company_size = Column(String(50))
    verification_status = Column(String(50))
    location = Column(String(100))


# ========== JOB & APPLICATION ==========
class Category(BaseModel):
    name = Column(String(50), nullable=False)
    description = Column(String(255), nullable=True)
    jobs = relationship("JobPosting", backref="category", lazy=True)

    # def __str__(self):
    #     return self.name



class JobPosting(BaseModel):
    title = Column(String(100))
    description = Column(Text)
    requirements = Column(Text)
    location = Column(String(100))
    salary = Column(Integer)
    employment_type = Column(String(50))
    status = Column(Enum(JobStatusEnum), default=JobStatusEnum.DRAFT.value)
    expiration_date = Column(DateTime)
    created_date = Column(DateTime, default=datetime.now())
    updated_date = Column(DateTime)
    view_count = Column(Integer, default=0)
    recruiter_id = Column(Integer, ForeignKey("recruiter.id"))
    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)

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
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    file_path = Column(String(255), nullable=False)
    is_default = Column(Boolean, default=False)
    created_date = Column(DateTime, default=datetime.now())
    updated_date = Column(DateTime)
    job_seeker_id = Column(Integer, ForeignKey('job_seeker.id'))

    job_seeker = relationship("JobSeeker", backref="resumes")

class Application(BaseModel):
    cover_letter = Column(Text)
    status = Column(String(20), default=ApplicationStatusEnum.DRAFT.value)
    applied_date = Column(DateTime, default=datetime.now())
    updated_date = Column(DateTime)
    feedback = Column(Text)
    resume_id = Column(Integer, ForeignKey('resume.id'))
    job_posting_id = Column(Integer, ForeignKey('job_posting.id'))

    resume = relationship("Resume")
    job_posting = relationship("JobPosting")

class Interview(BaseModel):
    dateTime = Column(DateTime)
    status = Column(String(20), default=InterviewStatusEnum.SCHEDULED.value)
    url = Column(String(255))
    application_id = Column(Integer, ForeignKey('application.id'))

    application = relationship("Application", backref="interviews", lazy=True)

# ========== CHAT ==========
class Conversation(BaseModel):
    created_date = Column(DateTime, default=datetime.now())

class Chat(BaseModel):
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.now())
    is_read = Column(Boolean, default=False)
    conversation_id = Column(Integer, ForeignKey('conversation.id'))
    sender_id = Column(Integer, ForeignKey('user.id'))

    conversation = relationship("Conversation", backref="chats", lazy=True)
    sender = relationship("User")

# ========== NOTIFICATION ==========
class Notification(BaseModel):
    content = Column(Text)
    is_read = Column(Boolean, default=False)
    created_date = Column(DateTime, default=datetime.now())
    user_id = Column(Integer, ForeignKey('user.id'))

    user = relationship("User", backref="notifications")

class NotificationChannel(BaseModel):
    channel_type = Column(String(50))
    status = Column(String(50))
    sent_at = Column(DateTime)
    notification_id = Column(Integer, ForeignKey('notification.id'))

    notification = relationship("Notification", backref="channels")


if __name__ == '__main__':
    with app.app_context():
        db.drop_all()  # Use with caution, this will delete all data
        db.create_all()
        # print(RoleEnum.JOBSEEKER.value=="JobSeeker")