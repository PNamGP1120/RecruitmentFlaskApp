import unittest
import hashlib
from unittest.mock import patch
from app import app, db
from app.models import User, RoleEnum, Job, JobStatusEnum, Company, Category, EmploymentEnum, Application, CV, Resume, \
    ApplicationStatusEnum
from app import dao


class TestDaoExtendedFunctions(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        # --- Dữ liệu mẫu ---
        password = 'password123'
        hashed_password = hashlib.md5(password.encode()).hexdigest()

        self.recruiter_user = User(username='recruiter_test', password=hashed_password, email='recruiter@test.com',
                                   role=RoleEnum.RECRUITER)
        self.jobseeker_user = User(username='jobseeker_test', password=hashed_password, email='jobseeker@test.com',
                                   role=RoleEnum.JOBSEEKER)
        db.session.add_all([self.recruiter_user, self.jobseeker_user])
        db.session.commit()

        self.company = Company(user_id=self.recruiter_user.id, company_name='TestCorp')
        db.session.add(self.company)
        db.session.commit()

        self.category_it = Category(name='IT')
        self.category_marketing = Category(name='Marketing')
        db.session.add_all([self.category_it, self.category_marketing])
        db.session.commit()

        self.job_posted = Job(title='Python Dev', location='HCMC', status=JobStatusEnum.POSTED,
                              company_id=self.company.id, category_id=self.category_it.id,
                              employment_type=EmploymentEnum.FULLTIME, salary=2000)
        self.job_draft = Job(title='Marketing Intern', location='Hanoi', status=JobStatusEnum.DRAFT,
                             company_id=self.company.id, category_id=self.category_marketing.id,
                             employment_type=EmploymentEnum.PARTTIME, salary=500)
        db.session.add_all([self.job_posted, self.job_draft])
        db.session.commit()

        self.resume = Resume(user_id=self.jobseeker_user.id, skill="Python")
        db.session.add(self.resume)
        db.session.commit()

        self.cv = CV(title="My Main CV", file_path="/fake/path.pdf", resume_id=self.resume.id)
        db.session.add(self.cv)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # --- Test Cases cho hàm add_user (trường hợp lỗi) ---
    def test_add_user_fail_username_exists(self):
        """Kiểm tra thêm người dùng thất bại khi username đã tồn tại."""
        user_data = {'username': 'jobseeker_test', 'password': 'pw', 'email': 'new@email.com'}
        new_user = dao.add_user(avatar_file=None, **user_data)
        self.assertIsNone(new_user)

    def test_add_user_fail_email_exists(self):
        """Kiểm tra thêm người dùng thất bại khi email đã tồn tại."""
        user_data = {'username': 'newuser', 'password': 'pw', 'email': 'jobseeker@test.com'}
        new_user = dao.add_user(avatar_file=None, **user_data)
        self.assertIsNone(new_user)

    # --- Test Cases cho các hàm count ---
    def test_count_candidates(self):
        """Kiểm tra đếm số lượng ứng viên (JOBSEEKER)."""
        count = dao.count_candidates()
        self.assertEqual(count, 1)

    def test_count_companies(self):
        """Kiểm tra đếm số lượng công ty (RECRUITER)."""
        count = dao.count_companies()
        self.assertEqual(count, 1)

    # --- Test Cases mở rộng cho load_jobs ---
    def test_load_jobs_by_category(self):
        """Kiểm tra lọc công việc theo danh mục."""
        jobs_pagination = dao.load_jobs(category_id=self.category_marketing.id)
        self.assertEqual(len(jobs_pagination.items), 0)  # Vì job marketing đang là DRAFT

    def test_load_jobs_by_employment_type(self):
        """Kiểm tra lọc công việc theo loại hình làm việc."""
        jobs_pagination = dao.load_jobs(employment_type=EmploymentEnum.FULLTIME)
        self.assertEqual(len(jobs_pagination.items), 1)
        self.assertEqual(jobs_pagination.items[0].title, 'Python Dev')

    def test_load_jobs_by_salary_range(self):
        """Kiểm tra lọc công việc theo khoảng lương."""
        jobs_pagination_min = dao.load_jobs(min_salary=1500)
        self.assertEqual(len(jobs_pagination_min.items), 1)
        jobs_pagination_max = dao.load_jobs(max_salary=1000)
        self.assertEqual(len(jobs_pagination_max.items), 0)

    def test_load_jobs_with_status(self):
        """Kiểm tra tải công việc với status cụ thể (DRAFT)."""
        jobs_pagination = dao.load_jobs(status=JobStatusEnum.DRAFT)
        self.assertEqual(len(jobs_pagination.items), 1)
        self.assertEqual(jobs_pagination.items[0].title, 'Marketing Intern')

    # --- Test Cases cho hàm add_job ---
    def test_add_job_success(self):
        """Kiểm tra thêm công việc mới thành công."""
        job_data = {
            'title': 'New QA Engineer',
            'description': 'Test everything',
            'requirements': 'Be careful',
            'location': 'Remote',
            'salary': 2500,
            'employment_type': 'FULLTIME',
            'status': JobStatusEnum.POSTED,
            'category_id': self.category_it.id
        }
        new_job = dao.add_job(company_id=self.company.id, **job_data)
        self.assertIsNotNone(new_job)
        self.assertEqual(new_job.title, 'New QA Engineer')

        # Kiểm tra lại tổng số job POSTED
        count = dao.count_jobs()
        self.assertEqual(count, 2)

    # --- Test Cases cho Application ---
    def test_load_applications_for_user(self):
        """Kiểm tra tải danh sách đơn ứng tuyển của một người dùng."""
        # Tạo một đơn ứng tuyển
        app1 = Application(cv_id=self.cv.id, job_id=self.job_posted.id, status=ApplicationStatusEnum.PENDING)
        db.session.add(app1)
        db.session.commit()

        # Tải đơn
        apps_pagination = dao.load_applications_for_user(self.jobseeker_user, page=1, per_page=5)
        self.assertEqual(len(apps_pagination.items), 1)
        self.assertEqual(apps_pagination.items[0].job.title, 'Python Dev')

    def test_load_applications_for_company(self):
        """Kiểm tra tải danh sách đơn ứng tuyển của một công ty."""
        app1 = Application(cv_id=self.cv.id, job_id=self.job_posted.id, status=ApplicationStatusEnum.PENDING)
        db.session.add(app1)
        db.session.commit()

        apps_pagination = dao.load_applications_for_company(user_id=self.recruiter_user.id, page=1, per_page=5)
        self.assertEqual(len(apps_pagination.items), 1)
        self.assertEqual(apps_pagination.items[0].status, ApplicationStatusEnum.PENDING)


if __name__ == '__main__':
    unittest.main()