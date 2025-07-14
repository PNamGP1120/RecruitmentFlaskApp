from idlelib.query import Query

from sqlalchemy import or_

from app import db, app
from app.models import User, Resume, Company, CV, Job, Application, Interview, Conversation, Message, Notification, \
    JobStatusEnum, Category, EmploymentEnum


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

if __name__ == "__main__":
    with app.app_context():
        u = load_jobs(location="Ha Noi City",employment_type=EmploymentEnum.FULLTIME)
        for i in u:
            print(i.title)
        # print(u.items.employment_type)
