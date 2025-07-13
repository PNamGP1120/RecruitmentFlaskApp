# from app import db
# from models import JobPosting, Recruiter, Category, JobStatusEnum
# from sqlalchemy import or_
# from datetime import datetime
#
# def get_job_postings(q=None, location=None, category_id=None, employment_type=None, page=1, per_page=10):
#     """
#     Lấy danh sách các bài đăng công việc với khả năng lọc và tìm kiếm.
#
#     :param q: Từ khóa tìm kiếm trong tiêu đề, mô tả, yêu cầu hoặc tên công ty.
#     :param location: Địa điểm làm việc.
#     :param category_id: ID của danh mục công việc.
#     :param employment_type: Loại hình công việc (ví dụ: 'Full-time', 'Part-time').
#     :param page: Số trang hiện tại cho phân trang.
#     :param per_page: Số lượng công việc trên mỗi trang.
#     :return: Một đối tượng Pagination chứa các bài đăng công việc.
#     """
#     query = db.session.query(JobPosting).filter(JobPosting.status == JobStatusEnum.ACTIVE.value)
#
#     # Lọc theo từ khóa tìm kiếm
#     if q:
#         search_term = f"%{q.lower()}%"
#         query = query.join(Recruiter).filter(
#             or_(
#                 JobPosting.title.ilike(search_term),
#                 JobPosting.description.ilike(search_term),
#                 JobPosting.requirements.ilike(search_term),
#                 Recruiter.company_name.ilike(search_term) # Tìm kiếm cả trong tên công ty
#             )
#         )
#
#     if location:
#         query = query.filter(JobPosting.location.ilike(f"%{location}%"))
#
#     if category_id:
#         query = query.filter(JobPosting.category_id == category_id)
#
#     if employment_type:
#         query = query.filter(JobPosting.employment_type.ilike(f"%{employment_type}%"))
#
#     query = query.order_by(JobPosting.created_date.desc())
#
#     job_postings = query.paginate(page=page, per_page=per_page, error_out=False)
#
#     return job_postings
#
# # if __name__ == '__main__':
# #     from app import app
# #     with app.app_context():
# #         print("--- Testing get_job_postings ---")
# #
# #         # Lấy tất cả các công việc đang hoạt động (trang 1, 5 công việc mỗi trang)
# #         all_jobs_page1 = get_job_postings(page=1, per_page=5)
# #         print(f"\nTổng số công việc đang hoạt động: {all_jobs_page1.total}")
# #         for job in all_jobs_page1.items:
# #             print(f"- {job.title} ({job.location}) by {job.recruiter.company_name} (Category: {job.category.name})")
# #
# #         # Tìm kiếm công việc "Engineer" ở "Ho Chi Minh City"
# #         engineer_jobs = get_job_postings(q="Engineer", location="Ho Chi Minh City")
# #         print(f"\nCông việc Engineer ở Ho Chi Minh City ({engineer_jobs.total} kết quả):")
# #         for job in engineer_jobs.items:
# #             print(f"- {job.title} ({job.location})")
# #
# #         # Tìm kiếm công việc "Marketing" trong danh mục "Marketing"
# #         marketing_jobs = get_job_postings(q="Digital", category_id=2) # Giả sử ID danh mục Marketing là 2
# #         print(f"\nCông việc Marketing trong danh mục Marketing ({marketing_jobs.total} kết quả):")
# #         for job in marketing_jobs.items:
# #             print(f"- {job.title} (Category ID: {job.category_id})")
# #
# #         # Lấy công việc Full-time
# #         fulltime_jobs = get_job_postings(employment_type="Full-time")
# #         print(f"\nCông việc Full-time ({fulltime_jobs.total} kết quả):")
# #         for job in fulltime_jobs.items:
# #             print(f"- {job.title} ({job.employment_type})")