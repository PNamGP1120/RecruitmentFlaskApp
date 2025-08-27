from sqlalchemy import Column, Integer, ForeignKey, String, Enum, DateTime, Boolean, Text, Float
from sqlalchemy.orm import relationship, backref
from app import db, app
from datetime import datetime, timedelta
from enum import Enum as MyEnum
from flask_login import UserMixin



# ========== ENUM KHAI BÁO ==========
class RoleEnum(MyEnum):
    ADMIN = "Admin"
    JOBSEEKER = "JobSeeker"
    RECRUITER = "Recruiter"

class EmploymentEnum(MyEnum):
    FULLTIME = "Fulltime"
    PARTTIME = "Parttime"

class JobStatusEnum(MyEnum):
    DRAFT = "Draft"
    POSTED = "Posted"
    DELETED = "Deleted"
    EXPIRED = "Expired"

class ApplicationStatusEnum(MyEnum):
    DRAFT = "Draft"
    PENDING = "Pending"
    REJECTED = "Rejected"
    CONFIRMED = "Confirmed"
    ACCEPTED = "Accepted"
    DELETED = "Deleted"


# ========== BASE MODEL ==========
class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id}>"



# ========== USER & RELATED ==========
class User(BaseModel, UserMixin):
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100), unique=True, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.JOBSEEKER.value)
    avatar = Column(Text, default='https://res.cloudinary.com/dqpu49bbo/image/upload/v1748718255/avatars/ecy9awxxse7npwq2sqwj.jpg')
    joined_date = Column(DateTime, default=datetime.now())
    phone = Column(String(20))
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    is_recruiter = Column(Boolean, default=False)

    conversation = relationship("Conversation", secondary='conversation_user', lazy='subquery', backref=backref('users', lazy=True))


class Resume(BaseModel):
    user_id = Column(Integer, ForeignKey('user.id'))
    skill = Column(String(255))
    experience = Column(String(255))
    education = Column(String(255))
    preferred_locations = Column(String(255))
    preferred_job_types = Column(String(255))
    linkedin_url = Column(String(255))
    user = relationship("User", backref=backref("resume", uselist=False))

class Company(BaseModel):
    user_id = Column(Integer, ForeignKey('user.id'), unique=True)
    website = Column(String(255))
    introduction = Column(Text)
    company_name = Column(String(255))
    industry = Column(String(100))
    company_size = Column(String(50))
    address = Column(String(100))

    user = relationship("User", backref=backref("company", uselist=False))
    jobs = relationship('Job', backref='company', lazy=True)


# ========== JOB & APPLICATION ==========
class Category(BaseModel):
    name = Column(String(50), nullable=False)
    description = Column(String(255), nullable=True)
    jobs = relationship("Job", backref="category", lazy=True)

    def __str__(self):
        return self.name



class Job(BaseModel):
    title = Column(String(100))
    description = Column(Text)
    requirements = Column(Text)
    location = Column(String(100))
    salary = Column(Float)
    employment_type = Column(Enum(EmploymentEnum))
    status = Column(Enum(JobStatusEnum), default=JobStatusEnum.DRAFT.value)
    expiration_date = Column(DateTime)
    created_date = Column(DateTime, default=datetime.now())
    updated_date = Column(DateTime)
    view_count = Column(Integer, default=0)
    company_id = Column(Integer, ForeignKey('company.id'))
    category_id = Column(Integer, ForeignKey("category.id"))



    def __str__(self):
        return self.title

class CV(BaseModel):
    __tablename__ = 'cv'
    title = Column(String(100), nullable=False)
    file_path = Column(String(255), nullable=False)
    is_default = Column(Boolean, default=False)
    created_date = Column(DateTime, default=datetime.now())
    updated_date = Column(DateTime)
    resume_id = Column(Integer, ForeignKey('resume.id'))

    resume = relationship("Resume", backref="cvs", lazy=True)

class Application(BaseModel):
    cover_letter = Column(Text)
    status = Column(Enum(ApplicationStatusEnum), default=ApplicationStatusEnum.DRAFT.value)
    applied_date = Column(DateTime, default=datetime.now())
    updated_date = Column(DateTime)
    feedback = Column(Text)
    cv_id = Column(Integer, ForeignKey('cv.id'))
    job_id = Column(Integer, ForeignKey('job.id'))

    cv = relationship("CV", backref="applications", lazy=True)
    job = relationship("Job", backref="applications", lazy=True)

class Interview(BaseModel):
    dateTime = Column(DateTime)
    url = Column(String(255))
    application_id = Column(Integer, ForeignKey('application.id'))
    application = relationship("Application", backref="interviews", lazy=True)

# ========== CHAT ==========
class Conversation(BaseModel):
    created_date = Column(DateTime, default=datetime.now())

class Message(BaseModel):
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.now())
    is_read = Column(Boolean, default=False)
    conversation_id = Column(Integer, ForeignKey('conversation.id'))
    sender_id = Column(Integer, ForeignKey('user.id'))

    conversation = relationship("Conversation", backref="messages", lazy=True)
    sender = relationship("User", backref="messages", lazy=True)

# ========== MIDDLE TABLE ==========
conversation_user = db.Table(
    'conversation_user',
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('conversation_id', Integer, ForeignKey('conversation.id'))
)

tag_job = db.Table("tag_job",
                   Column("tag_id", Integer, ForeignKey('tag.id')),
                   Column("job_id", Integer, ForeignKey('job.id')))

# ========== NOTIFICATION ==========
class Notification(BaseModel):
    content = Column(Text)
    is_read = Column(Boolean, default=False)
    created_date = Column(DateTime, default=datetime.now())
    user_id = Column(Integer, ForeignKey('user.id'))

    user = relationship("User", backref="notifications", lazy=True)


class Tag(BaseModel):
    name = Column(String(50))
    jobs = relationship("Job", secondary="tag_job", backref="tags", lazy=True)
    def __str__(self):
        return self.name



if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        # c1 = Category(name="Front-end")
        # c2 = Category(name="Back-end")
        # c3 = Category(name="FullStack")
        #
        # db.session.add_all([c1, c2, c3])
        # db.session.commit()

        # import hashlib
        # u1 = User(username="Admin", password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()), role=RoleEnum.ADMIN, email="admin@gmail.com" )
        # u2 = User(username="JopSeeker1", password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()), role=RoleEnum.JOBSEEKER, email="jobseeker1@gmail.com" )
        # u3 = User(username="Recruiter1", password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()), role=RoleEnum.RECRUITER, email="recruiter1@gmail.com" )
        #
        # db.session.add_all([u1, u2, u3])
        # db.session.commit()
        # u4 = User(username="Recruiter2", password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()), role=RoleEnum.RECRUITER.value, email="recruiter2@gmail.com" )
        # db.session.add(u4)
        # db.session.commit()
        #
        # print("Role: ", RoleEnum.JOBSEEKER)
        # print("Role.value: ", type(RoleEnum.JOBSEEKER.value))

        # # ===== COMPANY =====
        # company = Company(
        #     user_id=3,
        #     website="https://example.com",
        #     introduction="A leading tech company",
        #     company_name="ExampleTech",
        #     industry="IT",
        #     company_size="100-500",
        #     address="123 Tech Avenue"
        # )
        # db.session.add(company)
        # db.session.commit()
        #
        # # ===== JOB =====
        # job = Job(
        #     title="React Developer",
        #     description="Develop modern front-end apps",
        #     requirements="3+ years React experience",
        #     location="Ho Chi Minh City",
        #     salary=1500.0,
        #     employment_type=EmploymentEnum.FULLTIME,
        #     status=JobStatusEnum.POSTED,
        #     expiration_date=datetime.now() + timedelta(days=30),
        #     company_id=1,
        #     category_id=1
        # )
        # job1 = Job(
        #     title="C++ Developer",
        #     description="Develop modern front-end apps",
        #     requirements="3+ years React experience",
        #     location="Ho Chi Minh City",
        #     salary=1500.0,
        #     employment_type=EmploymentEnum.FULLTIME,
        #     status=JobStatusEnum.POSTED,
        #     expiration_date=datetime.now() + timedelta(days=30),
        #     company_id=1,
        #     category_id=1
        # )
        # job2 = Job(
        #     title="C# Developer",
        #     description="Develop modern front-end apps",
        #     requirements="3+ years React experience",
        #     location="Phu Quoc City",
        #     salary=1500.0,
        #     employment_type=EmploymentEnum.FULLTIME,
        #     status=JobStatusEnum.POSTED,
        #     expiration_date=datetime.now() + timedelta(days=30),
        #     company_id=1,
        #     category_id=1
        # )
        # job3 = Job(
        #     title="Python Developer",
        #     description="Develop modern front-end apps",
        #     requirements="3+ years React experience",
        #     location="Ho Chi Minh City",
        #     salary=1500.0,
        #     employment_type=EmploymentEnum.FULLTIME,
        #     status=JobStatusEnum.POSTED,
        #     expiration_date=datetime.now() + timedelta(days=30),
        #     company_id=1,
        #     category_id=1
        # )
        # job4 = Job(
        #     title="Java Developer",
        #     description="Develop modern front-end apps",
        #     requirements="3+ years React experience",
        #     location="Ha Noi City",
        #     salary=1500.0,
        #     employment_type=EmploymentEnum.FULLTIME,
        #     status=JobStatusEnum.POSTED,
        #     expiration_date=datetime.now() + timedelta(days=30),
        #     company_id=1,
        #     category_id=1
        # )
        # job5 = Job(
        #     title="Django Developer",
        #     description="Develop modern front-end apps",
        #     requirements="3+ years React experience",
        #     location="Da Nang City",
        #     salary=1500.0,
        #     employment_type=EmploymentEnum.FULLTIME,
        #     status=JobStatusEnum.POSTED,
        #     expiration_date=datetime.now() + timedelta(days=30),
        #     company_id=1,
        #     category_id=1
        # )
        # db.session.add_all([job, job1,job2,job3,job4,job5])
        # db.session.commit()
        #
        # job6 = Job(
        #     title="Django Developer",
        #     description="Develop modern front-end apps",
        #     requirements="3+ years React experience",
        #     location="Da Nang City",
        #     salary=1500.0,
        #     employment_type=EmploymentEnum.FULLTIME.value,
        #     status=JobStatusEnum.POSTED,
        #     expiration_date=datetime.now() + timedelta(days=30),
        #     company_id=1,
        #     category_id=1
        # )
        # db.session.add(job6)
        # db.session.commit()
        #
        # # ===== RESUME & CV =====
        # resume = Resume(
        #     user_id=2,
        #     skill="React, JavaScript, HTML, CSS",
        #     experience="2 years at WebXYZ",
        #     education="Bachelor of Computer Science",
        #     preferred_locations="Ho Chi Minh",
        #     preferred_job_types="Fulltime",
        #     linkedin_url="https://linkedin.com/in/johndoe"
        # )
        # db.session.add(resume)
        # db.session.commit()

        print("Dữ liệu mẫu đã được tạo thành công!")