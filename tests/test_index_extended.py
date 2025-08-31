import unittest
import hashlib
from app import app, db
from app.models import User, RoleEnum, Job, JobStatusEnum, Company, Category, Resume, CV
from unittest.mock import patch


class TestIndexExtendedRoutes(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        # --- Dữ liệu mẫu ---
        password = 'password123'
        hashed_password = hashlib.md5(password.encode()).hexdigest()

        self.jobseeker = User(username='jobseeker', password=hashed_password, email='jobseeker@test.com',
                              role=RoleEnum.JOBSEEKER)
        self.recruiter = User(username='recruiter', password=hashed_password, email='recruiter@test.com',
                              role=RoleEnum.RECRUITER)
        self.admin = User(username='admin', password=hashed_password, email='admin@test.com', role=RoleEnum.ADMIN)
        db.session.add_all([self.jobseeker, self.recruiter, self.admin])
        db.session.commit()

        self.company = Company(user_id=self.recruiter.id, company_name='Recruiter Corp')
        db.session.add(self.company)
        db.session.commit()

        self.category = Category(name='Testing')
        db.session.add(self.category)
        db.session.commit()

        self.job = Job(title='Automation Tester', company_id=self.company.id, category_id=self.category.id,
                       status=JobStatusEnum.POSTED)
        db.session.add(self.job)
        db.session.commit()

        self.resume = Resume(user_id=self.jobseeker.id, skill="Selenium")
        db.session.add(self.resume)
        db.session.commit()

        self.cv = CV(title="CV for Testing", file_path="/fake/path.pdf", resume_id=self.resume.id)
        db.session.add(self.cv)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, username, password):
        return self.client.post('/login', data=dict(username=username, password=password), follow_redirects=True)

    # --- Test Cases cho Register ---
    def test_register_page_loads(self):
        """Kiểm tra trang đăng ký (GET) tải thành công."""
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create Your Account', response.data)

    def test_register_success(self):
        """Kiểm tra đăng ký (POST) thành công."""
        response = self.client.post('/register', data=dict(
            username='newuser',
            password='newpassword',
            confirm_password='newpassword',
            email='new@email.com',
            role='JOBSEEKER'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Account Login', response.data)  # Chuyển hướng đến trang login

    def test_register_password_mismatch(self):
        """Kiểm tra đăng ký (POST) thất bại do mật khẩu không khớp."""
        response = self.client.post('/register', data=dict(
            username='newuser',
            password='newpassword',
            confirm_password='wrongpassword',
            email='new@email.com'
        ), follow_redirects=True)
        self.assertIn(b'Passwords do not match', response.data)

    # --- Test Cases cho Logout ---
    def test_logout(self):
        """Kiểm tra đăng xuất thành công."""
        self.login('jobseeker', 'password123')
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Account Login', response.data)
        self.assertNotIn(b'Logout', response.data)

    # --- Test Cases cho Job list và Job detail ---
    def test_job_list_page(self):
        """Kiểm tra trang danh sách công việc."""
        response = self.client.get('/jobs')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Automation Tester', response.data)

    def test_job_detail_page(self):
        """Kiểm tra trang chi tiết công việc."""
        response = self.client.get(f'/job-detail/{self.job.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Automation Tester', response.data)

    # --- Test Cases cho API ---
    def test_api_apply_job_success(self):
        """Kiểm tra API ứng tuyển công việc thành công."""
        self.login('jobseeker', 'password123')
        response = self.client.post(f'/api/apply/{self.job.id}', data=dict(
            coverLetter='I am interested',
            cv=self.cv.id
        ))
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data['message'], 'You have successfully applied')

    def test_api_apply_job_unauthorized(self):
        """Kiểm tra API ứng tuyển khi chưa đăng nhập."""
        response = self.client.post(f'/api/apply/{self.job.id}')
        self.assertEqual(response.status_code, 401)  # Bị login_required redirect

    def test_api_apply_job_as_recruiter(self):
        """Kiểm tra API ứng tuyển với vai trò Recruiter."""
        self.login('recruiter', 'password123')
        response = self.client.post(f'/api/apply/{self.job.id}', data=dict(
            coverLetter='I am recruiter',
            cv='1'
        ))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json()['message'], 'You are not a job seeker!')

    def test_api_verified_recruiter_as_admin(self):
        """Kiểm tra API xác thực recruiter bởi Admin."""
        self.login('admin', 'password123')
        # Ban đầu recruiter chưa được xác thực
        self.assertFalse(self.recruiter.is_recruiter)

        response = self.client.post(f'/api/verified-recruiter/{self.recruiter.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['status'], 200)

        # Kiểm tra lại trong DB
        user = User.query.get(self.recruiter.id)
        self.assertTrue(user.is_recruiter)

    def test_api_verified_recruiter_as_non_admin(self):
        """Kiểm tra API xác thực recruiter bởi người không phải Admin."""
        self.login('jobseeker', 'password123')
        response = self.client.post(f'/api/verified-recruiter/{self.recruiter.id}')
        self.assertEqual(response.status_code, 200)  # Route trả về JSON dù lỗi
        self.assertEqual(response.get_json()['status'], 403)


if __name__ == '__main__':
    unittest.main()