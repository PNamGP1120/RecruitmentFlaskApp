import hashlib
from datetime import datetime
from itertools import groupby

import cloudinary.uploader
from flask_login import current_user
from oauthlib.uri_validate import query

from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from app import db, app
from app.models import User, Resume, Company, CV, Job, Application, Interview, Conversation, Message, Notification, \
    JobStatusEnum, Category, EmploymentEnum, RoleEnum, ApplicationStatusEnum
from sqlalchemy import func, extract
import string, random


def load_cate():
    cates = Category.query.order_by("id").all()
    return cates


def load_jobs(
        page=None,
        per_page=None,
        keyword=None,
        location=None,
        employment_type=None,
        category_id=None,
        company_id=None,
        min_salary=None,
        max_salary=None,
        status=JobStatusEnum.POSTED,
        exclude_job=None
):
    """
    Tải danh sách các công việc với chức năng lọc, tìm kiếm và phân trang.

    :param exclude_job:
    :param page: Số trang hiện tại (mặc định 1).
    :param per_page: Số lượng công việc trên mỗi trang (mặc định 10)
    :param keyword: Từ khóa để tìm kiếm trong tiêu đề, mô tả, yêu cầu.
    :param location: Địa điểm công việc.
    :param employment_type: Loại hình việc làm (ví dụ: "Fulltime", "Parttime").
    :param category_id: ID của danh mục công việc.
    :param company_id: ID của công ty.
    :param min_salary: Mức lương tối thiểu.
    :param max_salary: Mức lương tối đa.
    :param status: Trạng thái công việc (mặc định là 'Posted').
    :return: Đối tượng phân trang (Pagination object) chứa các công việc.
    """

    query = Job.query.filter()

    if status:
        query = query.filter(Job.status == status)

    if keyword:
        query = query.filter(Job.title.contains(keyword))

    if location:
        query = query.filter(Job.location.contains(location))

    if employment_type:
        query = query.filter(Job.employment_type == employment_type)

    if category_id:
        query = query.filter(Job.category_id == category_id)

    if company_id:
        query = query.filter(Job.company_id == company_id)

    if min_salary is not None:
        query = query.filter(Job.salary >= min_salary)

    if max_salary is not None:
        query = query.filter(Job.salary <= max_salary)

    if employment_type:
        try:
            # Chuyển string sang enum
            emp_enum = EmploymentEnum[employment_type]  # "FULLTIME" => EmploymentEnum.FULLTIME
            print(emp_enum.name)
            query = query.filter(Job.employment_type == emp_enum)
        except KeyError:
            pass  # không lọc nếu sai

    if exclude_job:
        query = query.filter(Job.id != exclude_job)

    query = query.order_by(Job.created_date.desc())
    jobs_pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    print("a", jobs_pagination.items)
    print(query.statement.compile(compile_kwargs={"literal_binds": True}))

    return jobs_pagination


def add_job(company_id, **job_data):
    """
    Thêm một công việc mới vào cơ sở dữ liệu.
    :param company_id:
    :param job_data: Dictionary chứa các dữ liệu công việc từ form, bao gồm:
                    title, description, requirements, location, employment_type (chuỗi),
                    category_id, company_id, salary, và bất kỳ trường nào khác bạn đã thêm vào form.
    :return: Đối tượng Job nếu thêm thành công, ngược lại là None.
    """
    title = job_data.get('title')
    description = job_data.get('description')
    requirements = job_data.get('requirements')
    location = job_data.get('location')
    salary = job_data.get('salary', 0)
    employment_type = job_data.get('employment_type', 'FULLTIME')
    status = job_data.get('status', JobStatusEnum.POSTED)
    category_id = job_data.get('category_id')
    is_active = job_data.get('is_active', True)

    job = Job(
        title=title,
        description=description,
        requirements=requirements,
        location=location,
        salary=salary,
        employment_type=employment_type,
        status=status,
        created_date=datetime.now(),
        updated_date=datetime.now(),
        category_id=int(category_id),
        company_id=company_id

    )
    print(category_id)
    print('jhgvcbuyiodsavbgfihljvbilofaedhgbvlhjsdgbhfilbdgljkfgblkjsdbfjiklhiutgfhijhiugioygouyguyifgvouyfvip')
    try:
        job.company_id = company_id
        db.session.add(job)
        db.session.commit()
        print(f"Đã thêm công việc: {title} thành công.")
        return job
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi thêm công việc vào DB: {e}")
        return None


def add_user(avatar_file, **user_data):
    """
    Thêm một người dùng mới vào cơ sở dữ liệu, xử lý upload avatar và các dữ liệu form.

    :param avatar_file: Đối tượng FileStorage từ request.files.get('avatar').
                        Có thể là None nếu người dùng không upload avatar.
    :param user_data: Dictionary chứa các dữ liệu người dùng từ form, bao gồm:
                      username, password, email, first_name, last_name, role (chuỗi),
                      và bất kỳ trường nào khác bạn đã thêm vào form.
    :return: Đối tượng User nếu thêm thành công, ngược lại là None.
    """

    username = user_data.get('username')
    password = user_data.get('password')
    email = user_data.get('email')
    first_name = user_data.get('first_name')
    last_name = user_data.get('last_name')
    role_str = user_data.get('role', 'JOBSEEKER')
    phone = user_data.get('phone')
    is_active = user_data.get('is_active', True)

    if User.query.filter_by(username=username).first():
        print(f"Lỗi: Tên đăng nhập '{username}' đã tồn tại.")
        return None
    if User.query.filter_by(email=email).first():
        print(f"Lỗi: Email '{email}' đã tồn tại.")
        return None

    hashed_password = hashlib.md5(password.encode()).hexdigest()

    role_enum_value = RoleEnum.JOBSEEKER
    try:
        role_enum_value = RoleEnum[role_str.upper()]
    except KeyError:
        print(f"Cảnh báo: Vai trò '{role_str}' không hợp lệ, đặt mặc định là JOBSEEKER.")

    new_user = User(
        username=username,
        password=hashed_password,
        email=email,
        first_name=first_name,
        last_name=last_name,
        role=role_enum_value,
        joined_date=datetime.now(),
        phone=phone,
        is_active=is_active
    )

    if avatar_file:
        try:
            if avatar_file.filename and avatar_file.content_type:
                res = cloudinary.uploader.upload(avatar_file.stream)
                new_user.avatar = res['secure_url']
                print(f"Đã upload avatar lên Cloudinary: {res['secure_url']}")
            else:
                print("Không có file avatar hợp lệ được gửi.")
                new_user.avatar = None  # Đặt avatar là None nếu file không hợp lệ
        except Exception as e:
            print(f"Lỗi khi upload avatar lên Cloudinary: {e}")
            new_user.avatar = None

    try:
        db.session.add(new_user)
        db.session.commit()
        print(f"Đã thêm người dùng: {username} ({role_enum_value.value}) thành công.")
        return new_user
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi thêm người dùng vào DB: {e}")
        return None


def add_user_google(**user_data):
    """
    Thêm một người dùng mới vào cơ sở dữ liệu từ dữ liệu đăng nhập Google.

    Hàm này không yêu cầu file upload và xử lý avatar_url trực tiếp.
    :param user_data: Dictionary chứa các dữ liệu người dùng:
                      username, email, first_name, last_name, role, password, avatar.
    :return: Đối tượng User nếu thêm thành công, ngược lại là None.
    """
    username = user_data.get('username')
    email = user_data.get('email')
    first_name = user_data.get('first_name')
    last_name = user_data.get('last_name')
    role_str = user_data.get('role', 'JOBSEEKER')
    password = user_data.get('password')
    avatar_url = user_data.get('avatar')

    # Xử lý mật khẩu
    # Sử dụng một placeholder an toàn vì người dùng Google không có mật khẩu
    hashed_password = hashlib.md5(password.encode()).hexdigest()

    # Chuyển chuỗi role thành đối tượng enum
    role_enum_value = RoleEnum.JOBSEEKER
    if role_str and isinstance(role_str, str):
        try:
            role_enum_value = RoleEnum[role_str.upper()]
        except KeyError:
            # Giữ giá trị mặc định nếu chuỗi không hợp lệ
            pass

    new_user = User(
        username=username,
        password=hashed_password,
        email=email,
        first_name=first_name,
        last_name=last_name,
        role=role_enum_value,
        joined_date=datetime.now(),
        avatar=avatar_url,
        is_active=True
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        print(f"Đã thêm người dùng Google: {username} thành công.")
        return new_user
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi thêm người dùng Google vào DB: {e}")
        return None


def get_user_by_email(email):
    """
    Tìm và trả về một đối tượng User dựa trên email của họ.
    :param email: Địa chỉ email của người dùng.
    :return: Đối tượng User nếu tìm thấy, ngược lại là None.
    """
    return User.query.filter_by(email=email).first()


def add_resume(resume):
    """
    Add a Resume object to the database.

    Args:
        resume (Resume): The Resume object to be saved.

    Returns:
        bool: True if the resume was added successfully, False otherwise.
    """
    try:
        resume.user_id = current_user.id
        db.session.add(resume)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error adding resume: {e}")
        return False


def update_resume(resume, data):
    """
    Update an existing Resume object in the database.

    Args:
        resume (Resume): The Resume object to update.
        data (dict): Dictionary containing the updated resume fields.

    Returns:
        bool: True if the resume was updated successfully, False otherwise.
    """
    try:
        for key, value in data.items():
            setattr(resume, key, value)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error updating resume: {e}")
        return False


def add_cv(title, file, is_default, resume_id=None):
    """
    Add a CV to the database and upload the file to Cloudinary.

    Args:
        title (str): The title of the CV.
        file: FileStorage object containing the CV file.
        is_default (bool): Whether this CV should be set as default.
        resume_id (int, optional): The ID of the associated resume.

    Returns:
        bool: True if the CV was added successfully, False otherwise.
    """
    try:
        # Upload file to Cloudinary
        upload_result = cloudinary.uploader.upload(file.stream)
        file_path = upload_result['secure_url']

        # If this CV is set as default, unset others for the same resume
        if is_default and resume_id:
            CV.query.filter_by(resume_id=resume_id, is_default=True).update({'is_default': False})

        # Create new CV
        cv = CV(
            title=title,
            file_path=file_path,
            is_default=is_default,
            resume_id=resume_id,
            created_date=datetime.now(),
            updated_date=datetime.now()
        )
        db.session.add(cv)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error adding CV: {e}")
        return False


def update_cv(cv, title, file, is_default, resume_id=None):
    """
    Update an existing CV in the database and optionally upload a new file to Cloudinary.

    Args:
        cv (CV): The CV object to update.
        title (str): The new title of the CV.
        file: FileStorage object containing the new CV file (optional).
        is_default (bool): Whether this CV should be set as default.
        resume_id (int, optional): The ID of the associated resume.

    Returns:
        bool: True if the CV was updated successfully, False otherwise.
    """
    try:
        cv.title = title
        cv.updated_date = datetime.now()

        # If a new file is provided, upload it
        if file:
            upload_result = cloudinary.uploader.upload(file.stream)
            cv.file_path = upload_result['secure_url']

        # If this CV is set as default, unset others for the same resume
        if is_default and resume_id:
            CV.query.filter_by(resume_id=resume_id, is_default=True).filter(CV.id != cv.id).update(
                {'is_default': False})
        cv.is_default = is_default

        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error updating CV: {e}")
        return False


def delete_cv(cv):
    """
    Delete a CV from the database.

    Args:
        cv (CV): The CV object to delete.

    Returns:
        bool: True if the CV was deleted successfully, False otherwise.
    """
    try:
        db.session.delete(cv)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting CV: {e}")
        return False


def is_company_exist(user_id):
    return Company.query.filter_by(user_id=user_id).first() is not None


def add_company(data_company):
    company = Company(**data_company)
    db.session.add(company)
    db.session.commit()
    return company


def update_company(company, data):
    for key, value in data.items():
        print(key, value)
        setattr(company, key, value)
    db.session.commit()
    return True


# def load_company_by_id(user_id):
#     return Company.query.filter_by(user_id=user_id).first()

def is_company_exist(user_id):
    return Company.query.filter_by(user_id=user_id).first() is not None


def add_company(data_company):
    company = Company(**data_company)
    db.session.add(company)
    db.session.commit()
    return company


def update_company(company, data):
    for key, value in data.items():
        print(key, value)
        setattr(company, key, value)
    db.session.commit()
    return True


def load_company_by_id(user_id):
    return Company.query.filter_by(user_id=user_id).first()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def get_user_by_application_id(application_id):
    application = Application.query.get(application_id)
    return application.cv.resume.user if application else None


def auth_user(username, password, role=None):
    user = User.query.filter_by(username=username).first()

    if user:
        hashed_input_password = hashlib.md5(password.encode()).hexdigest()
        if user.password == hashed_input_password:
            if role:
                if user.role == role:
                    return user
                else:
                    return None
            else:
                return user
    return None


def count_jobs():
    return db.session.query(Job).filter(Job.status == JobStatusEnum.POSTED).count()


def count_candidates():
    print(User.role)
    return db.session.query(User).filter(User.role == RoleEnum.JOBSEEKER, User.is_active == True).count()


def count_companies():
    return db.session.query(User).filter(User.role == RoleEnum.RECRUITER, User.is_active == True).count()


def load_cv_by_id(user_id):
    resume = Resume.query.filter_by(user_id=user_id).first()
    if not resume:
        return None
    return CV.query.filter_by(resume_id=resume.id).all()


def get_resume_by_user(user_id):
    return Resume.query.filter_by(user_id=user_id).first()


def get_cv_ids_by_resume(resume_id):
    cv_ids = db.session.query(CV.id).filter_by(resume_id=resume_id).all()
    return [id for (id,) in cv_ids]


def get_applications_by_cv_ids(cv_ids):
    return Application.query.filter(Application.cv_id.in_(cv_ids))


# Load cac don ung tuyen cua nguoi dung
def load_applications_for_user(current_user, page=None, per_page=None, status=None):
    if page and per_page:
        resume = get_resume_by_user(current_user.id)
        if not resume:
            return Application.query.filter(False).paginate(page=page, per_page=per_page)

        cv_ids = get_cv_ids_by_resume(resume.id)
        if not cv_ids:
            return Application.query.filter(False).paginate(page=page, per_page=per_page)

        applications = get_applications_by_cv_ids(cv_ids)
        if status:
            applications = applications.filter_by(status=status)
        return applications.paginate(page=page, per_page=per_page)
    return None


# load job cua cong ty
def get_job_by_company_id(company_id, year=None):
    query = db.session.query(Job.id).filter(Job.company_id == company_id)

    if year:
        query = query.filter(extract('year', Job.created_date) == year)
    job_ids = query.all()
    return [id for (id,) in job_ids]


# Lay danh sach cac don ung tuyen cua 1 job
def get_application_by_job(job_id):
    return Application.query.filter_by(job_id=job_id).all()


# lay danh sach cua tat ca job
def get_applications_by_job_ids(job_ids):
    return Application.query.filter(Application.job_id.in_(job_ids))


# load danh sach cac don ung tuyen cua mot cong ty (tat ca job)
def load_applications_for_company(user_id=None, page=None, per_page=None, status=None):
    if page and per_page:
        # lay thong tin cong ty
        company = load_company_by_id(user_id)
        if not company:
            return Application.query.filter(False).paginate(page=page, per_page=per_page)

        # lat job cua cong ty
        jobs = get_job_by_company_id(company.id)
        print(jobs)
        if not jobs:
            return Application.query.filter(False).paginate(page=page, per_page=per_page)

        applications = get_applications_by_job_ids(job_ids=jobs)
        if status:
            applications = applications.filter_by(status=status)
        print(applications)
        return applications.paginate(page=page, per_page=per_page)
    return None


def get_application_by_id(apply_id):
    return Application.query.get(apply_id)


class NotificationDAO:
    @staticmethod
    def create(user_id: int, content: str) -> Notification:
        new_notification = Notification(
            user_id=user_id,
            content=content,
            created_date=datetime.now()
        )
        db.session.add(new_notification)
        db.session.commit()
        return new_notification

    @staticmethod
    def get_all(user_id: int, page: int = 1, per_page: int = 10):
        return Notification.query.filter_by(user_id=user_id) \
            .order_by(Notification.created_date.desc()) \
            .paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_by_id(notification_id):
        return Notification.query.filter_by(id=notification_id).first()

    @staticmethod
    def get_unread(user_id: int) -> int:
        return Notification.query.filter_by(user_id=user_id, is_read=False).count()

    @staticmethod
    def mark_all_as_read(user_id: int) -> None:
        Notification.query.filter_by(user_id=user_id, is_read=False).update({
            "is_read": True
        })
        db.session.commit()

    @staticmethod
    def delete(notification_id: int) -> bool:
        noti = Notification.query.get(notification_id)
        if noti:
            db.session.delete(noti)
            db.session.commit()
            return True
        return False

    @staticmethod
    def delete_all_by_user(user_id: int) -> int:
        count = Notification.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        return count

    @staticmethod
    def mark_as_read(notification_id, user_id):
        notify = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if notify and not notify.is_read:
            notify.is_read = True
            db.session.commit()


def get_list_recruiter(page=None, per_page=None):
    query = User.query.filter_by(role=RoleEnum.RECRUITER, is_active=True)
    print("query:", query)
    listRecruiter_pagination = query.paginate(page=page, per_page=per_page)
    print(listRecruiter_pagination)
    return listRecruiter_pagination


def get_conversations_for_user(user_id):
    """Lấy tất cả các cuộc trò chuyện của một người dùng."""
    user = User.query.get(user_id)
    if user:
        return user.conversation
    return []


def get_conversation_by_id(conversation_id):
    return Conversation.query.get(conversation_id)


def get_or_create_conversation(user1_id, user2_id):
    conv = db.session.query(Conversation).filter(
        Conversation.users.any(id=user1_id),
        Conversation.users.any(id=user2_id)
    ).first()

    if conv:
        return conv
    else:
        user1 = User.query.get(user1_id)
        user2 = User.query.get(user2_id)
        if user1 and user2:
            new_conv = Conversation()
            new_conv.users.append(user1)
            new_conv.users.append(user2)
            db.session.add(new_conv)
            db.session.commit()
            return new_conv
    return None


def add_message(conversation_id, sender_id, content):
    message = Message(
        conversation_id=conversation_id,
        sender_id=sender_id,
        content=content
    )
    db.session.add(message)
    db.session.commit()
    return message


def stats_job_by_recruiter(company_id, time='month', year=datetime.now().year):
    return (
        db.session.query(
            func.extract(time, Job.created_date).label("month"),
            func.count(Job.id).label("count"),
            func.extract("year", Job.created_date).label("year")
        )
        .join(Company, Company.id == Job.company_id)
        .filter(Company.id == company_id)
        .filter(func.extract("year", Job.created_date) == year)
        .group_by(func.extract(time, Job.created_date), func.extract("year", Job.created_date))
        .order_by(func.extract(time, Job.created_date))
        .all()
    )


def stats_application_by_recruiter(job_id):
    job = db.session.query(Job).filter(Job.id == job_id).first()
    query = db.session.query(Application).filter(Application.job_id == job_id).count()
    return {"job_id": job.id, "title": job.title, "count": query}


def render_interview_link(application_id, prefix="application"):
    room = f"{prefix}_{application_id}_" + ''.join(random.choices(string.ascii_letters + string.digits, k=4))
    return f"https://meet.jit.si/{room}"


def create_interview_link(application_id, interview_date):
    query = db.session.query(Interview).filter(Interview.application_id == application_id).first()
    if not query:
        link = render_interview_link(application_id)
        interview = Interview(
            application_id=application_id,
            dateTime=interview_date,
            url=link
        )
        db.session.add(interview)
        db.session.commit()
        return link
    else:
        return query.url


def get_interview(application_id):
    query = db.session.query(Interview).filter(Interview.application_id == application_id).first()
    return query


def get_list_interview_by_owner_company(user_id):
    company= db.session.query(Company).filter(Company.user_id==user_id).first()
    if company:
        return (db.session.query(Interview)
                .join(Application, Interview.application_id == Application.id)
                .join(Job, Application.job_id == Job.id)
                .filter(Job.company_id == company.id)
                .options(
            joinedload(Interview.application) #joinedLoad giup han che bi N+1 query
            .joinedload(Application.job)
        ).all())
    return None


def get_company_by_id(company_id):
    return db.session.query(Company).filter(Company.id==company_id).first()

if __name__ == "__main__":
    with app.app_context():
        # u = load_jobs(location="Ha Noi City",employment_type=EmploymentEnum.FULLTIME)
        # for i in u:
        #     print(i.title)
        # print(u.items.employment_type)
        # a = get_application_by_job(2)
        # print(a)
        # ap = load_applications_for_company(2, page=1,per_page=3, status=ApplicationStatusEnum.PENDING)
        # for p in  range (1, ap.pages+1):
        #     app = load_applications_for_company(3,page=p, per_page=3)
        #     for a in app.items:
        #         print(a)
        # print("ap.itmes",ap.items)

        # print(count_candidates())
        print(get_company_by_id(company_id=3).company_name)

