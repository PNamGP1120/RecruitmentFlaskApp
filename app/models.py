from datetime import datetime
from enum import Enum as MyEnum
from app import app, db
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship, backref


class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id}>"

class Role(MyEnum):
    ADMIN = "Admin"
    JOBSEEKER = "JobSeeker"
    RECRUITER = "Recruiter"

conversation_user = db.Table('conversation_user',Column("user.id", ForeignKey('user.id')),Column('conversation.id', ForeignKey('conversation.id')))

class User(BaseModel):
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    email = Column(String(100), unique=True, nullable=False)
    role = Column(Enum(Role), default=Role.JOBSEEKER, nullable=False)
    avatar = Column(String(255), nullable=True)
    joined_date = Column(DateTime, default=datetime.utcnow)
    phone = Column(String(20), nullable=True)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    conversation = relationship("Conversation", secondary='conversation_user', lazy="subquery", backref=backref('users', lazy=True))

    def __repr__(self):
        return f"<User {self.username} - {self.role.value}>"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}" if self.first_name or self.last_name else self.username
    
    def is_admin(self):
        return self.role == Role.ADMIN

    def is_job_seeker(self):
        return self.role == Role.JOBSEEKER

    def is_recruiter(self):
        return self.role == Role.RECRUITER

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar
        return "https://www.gravatar.com/avatar/"
    
    def __str__(self):
        return self.get_full_name() if self.get_full_name() else self.username

class JobSeeker(db.Model):
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    skill = Column(String(255), nullable=True)
    experience= Column(String(255), nullable=True)
    education = Column(String(255), nullable=True)
    preferred_locations = Column(String(255), nullable=True)
    preferred_job_types = Column(String(255), nullable=True)
    linkedin_url = Column(String(255), nullable=True)
    user = relationship("User")


class Resume(BaseModel):
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    file_path = Column(String(255), nullable=False)
    is_default = Column(Boolean, default=False)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime)
    job_seeker_id = Column(Integer, ForeignKey('job_seeker.id'))


class Recruiter(db.Model):
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    website = Column(String(255))
    introduction = Column(Text)
    company_name = Column(String(255))
    industry = Column(String(100))
    company_size = Column(String(50))
    verification_status = Column(String(50))
    location = Column(String(100))
    user = relationship("User")


class JobStatus(MyEnum):
    DRAFT = "Draft"
    ACTIVE = "Active"
    CLOSED = "Closed"
    EXPIRED = "Expired"

class ApplicationStatus(MyEnum):
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    INTERVIEW = "Interview"
    REJECTED = "Rejected"
    ACCEPTED = "Accepted"

class InterviewStatus(MyEnum):
    SCHEDULED = "Scheduled"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class JobPosting(BaseModel):
    title = Column(String(100))
    description = Column(Text)
    requirements = Column(Text)
    location = Column(String(100))
    salary = Column(Integer)
    employment_type = Column(String(50))
    status = Column(Enum(JobStatus), default=JobStatus.EXPIRED)
    expiration_date = Column(DateTime)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime)
    view_count = Column(Integer, default=0)
    recruiter_id = Column(Integer, ForeignKey('recruiter.id'))

    def __str__(self):
        return self.title

class Application(BaseModel):
    cover_letter = Column(Text)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.DRAFT)
    applied_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime)
    feedback = Column(Text)
    resume_id = Column(Integer, ForeignKey('resume.id'))
    job_posting_id = Column(Integer, ForeignKey('job_posting.id'))


class Interview(BaseModel):
    dateTime = Column(DateTime)
    status = Column(Enum(InterviewStatus), default=InterviewStatus.SCHEDULED)
    url = Column(String(255))
    application_id = Column(Integer, ForeignKey('application.id'))


class Chat(BaseModel):
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    conversation_id = Column(Integer, ForeignKey('conversation.id'))
    sender_id = Column(Integer, ForeignKey('user.id'))


class Conversation(BaseModel):
    created_date = Column(DateTime, default=datetime.utcnow)




class Notification(BaseModel):
    content = Column(Text)
    is_read = Column(Boolean, default=False)
    created_date = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('user.id'))


class NotificationChannel(BaseModel):
    channel_type = Column(String(50))
    status = Column(String(50))
    sent_at = Column(DateTime)
    notification_id = Column(Integer, ForeignKey('notification.id'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()