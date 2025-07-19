import hashlib
from datetime import datetime

import cloudinary.uploader
from flask_login import current_user
from idlelib.query import Query

from sqlalchemy import or_

from app import db, app
from app.models import User, Resume, Company, CV, Job, Application, Interview, Conversation, Message, Notification, \
    JobStatusEnum, Category, EmploymentEnum, RoleEnum


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
):
    """
    Tải danh sách các công việc với chức năng lọc, tìm kiếm và phân trang.

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


    query = Job.query.filter(Job.status == status)

    if keyword:
        query = query.filter( Job.title.contains(keyword))

    if location :
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


    jobs_pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    print("a",jobs_pagination.items)
    print(query.statement.compile(compile_kwargs={"literal_binds": True}))

    return jobs_pagination


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
                new_user.avatar = None # Đặt avatar là None nếu file không hợp lệ
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

def is_company_exist(user_id):
    return Company.query.filter_by(user_id=user_id).first() is not None

def add_company(data_company):
    company = Company(**data_company)
    db.session.add(company)
    db.session.commit()
    return company

def update_company(company, data):
    for key, value in data.items():
        print(key,value)
        setattr(company, key, value)
    db.session.commit()
    return True

def load_company_by_id(user_id):
    return Company.query.filter_by(user_id=user_id).first()

def get_user_by_id(user_id):
    return User.query.get(user_id)


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
    return db.session.query(User).filter(User.role == RoleEnum.JOBSEEKER, User.is_active == True).count()

def count_companies():
    return db.session.query(User).filter(User.role == RoleEnum.RECRUITER, User.is_active == True).count()


if __name__ == "__main__":
    with app.app_context():
        u = load_jobs(location="Ha Noi City",employment_type=EmploymentEnum.FULLTIME)
        for i in u:
            print(i.title)
        # print(u.items.employment_type)
