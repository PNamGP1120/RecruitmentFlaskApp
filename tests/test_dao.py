import unittest
import hashlib
from unittest.mock import patch
from app import app, db
from app.models import User, RoleEnum, Job, JobStatusEnum, Company, Category, EmploymentEnum
from app import dao


class TestDaoFunctions(unittest.TestCase):

    def setUp(self):
        """
        Thiết lập môi trường test trước mỗi test case.
        - Sử dụng database SQLite trong bộ nhớ để test.
        - Tạo context cho ứng dụng Flask.
        - Tạo tất cả các bảng trong database.
        - Thêm dữ liệu mẫu để sử dụng trong các test case.
        """
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        # --- Thêm dữ liệu mẫu ---
        # 1. Tạo một người dùng (recruiter) để test
        password_recruiter = 'recruiter123'
        hashed_password = hashlib.md5(password_recruiter.encode()).hexdigest()
        self.recruiter_user = User(
            username='testrecruiter',
            password=hashed_password,
            email='recruiter@test.com',
            role=RoleEnum.RECRUITER
        )
        db.session.add(self.recruiter_user)
        db.session.commit()

        # 2. Tạo một công ty cho recruiter
        self.company = Company(
            user_id=self.recruiter_user.id,
            company_name='TestCorp'
        )
        db.session.add(self.company)
        db.session.commit()

        # 3. Tạo một danh mục
        self.category = Category(name='IT - Test')
        db.session.add(self.category)
        db.session.commit()

        # 4. Tạo một công việc
        self.job1 = Job(
            title='Python Developer Test',
            location='Ho Chi Minh City',
            status=JobStatusEnum.POSTED,
            company_id=self.company.id,
            category_id=self.category.id,
            employment_type=EmploymentEnum.FULLTIME
        )
        self.job2_draft = Job(
            title='Java Developer Draft',
            location='Ha Noi',
            status=JobStatusEnum.DRAFT,
            company_id=self.company.id,
            category_id=self.category.id,
            employment_type=EmploymentEnum.FULLTIME
        )
        db.session.add_all([self.job1, self.job2_draft])
        db.session.commit()

    def tearDown(self):
        """
        Dọn dẹp môi trường sau mỗi test case.
        - Xóa session database.
        - Xóa tất cả các bảng.
        - Hủy context của ứng dụng.
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # --- Test Cases cho hàm auth_user ---
    def test_auth_user_success(self):
        """Kiểm tra đăng nhập thành công với username và password đúng."""
        user = dao.auth_user('testrecruiter', 'recruiter123')
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testrecruiter')

    def test_auth_user_fail_wrong_password(self):
        """Kiểm tra đăng nhập thất bại với password sai."""
        user = dao.auth_user('testrecruiter', 'wrongpassword')
        self.assertIsNone(user)

    def test_auth_user_fail_wrong_username(self):
        """Kiểm tra đăng nhập thất bại với username không tồn tại."""
        user = dao.auth_user('nonexistentuser', 'recruiter123')
        self.assertIsNone(user)

    def test_auth_user_with_role_success(self):
        """Kiểm tra đăng nhập thành công khi yêu cầu đúng vai trò."""
        user = dao.auth_user('testrecruiter', 'recruiter123', role=RoleEnum.RECRUITER)
        self.assertIsNotNone(user)
        self.assertEqual(user.role, RoleEnum.RECRUITER)

    def test_auth_user_with_role_fail(self):
        """Kiểm tra đăng nhập thất bại khi yêu cầu sai vai trò."""
        user = dao.auth_user('testrecruiter', 'recruiter123', role=RoleEnum.JOBSEEKER)
        self.assertIsNone(user)

    # --- Test Cases cho hàm count_jobs ---
    def test_count_jobs(self):
        """Kiểm tra hàm đếm số công việc đang ở trạng thái POSTED."""
        # Trong setUp, chúng ta đã thêm 1 job POSTED và 1 job DRAFT
        count = dao.count_jobs()
        self.assertEqual(count, 1)

    # --- Test Cases cho hàm load_jobs ---
    def test_load_jobs_no_filter(self):
        """Kiểm tra tải danh sách công việc mà không có bộ lọc."""
        jobs_pagination = dao.load_jobs(page=1, per_page=5)
        self.assertEqual(len(jobs_pagination.items), 1)
        self.assertEqual(jobs_pagination.items[0].title, 'Python Developer Test')

    def test_load_jobs_by_keyword(self):
        """Kiểm tra tìm kiếm công việc theo từ khóa trong tiêu đề."""
        jobs_pagination = dao.load_jobs(keyword='Python', page=1, per_page=5)
        self.assertEqual(len(jobs_pagination.items), 1)
        self.assertEqual(jobs_pagination.items[0].title, 'Python Developer Test')

    def test_load_jobs_by_location(self):
        """Kiểm tra tìm kiếm công việc theo địa điểm."""
        jobs_pagination = dao.load_jobs(location='Ho Chi Minh', page=1, per_page=5)
        self.assertEqual(len(jobs_pagination.items), 1)

    def test_load_jobs_not_found(self):
        """Kiểm tra tìm kiếm công việc không có kết quả."""
        jobs_pagination = dao.load_jobs(keyword='Ruby', page=1, per_page=5)
        self.assertEqual(len(jobs_pagination.items), 0)

    # --- Test Case cho hàm add_user (sử dụng Mocking) ---
    @patch('app.dao.cloudinary.uploader.upload')
    def test_add_user_success(self, mock_upload):
        """
        Kiểm tra thêm người dùng mới thành công.
        Sử dụng @patch để "giả lập" hàm upload của Cloudinary,
        tránh việc phải thực sự upload file khi chạy test.
        """
        mock_upload.return_value = {'secure_url': 'http://mock.url/avatar.jpg'}

        user_data = {
            'username': 'newjobseeker',
            'password': 'password123',
            'email': 'new@jobseeker.com',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'JOBSEEKER'
        }

        # Hàm add_user nhận một đối số là file, ta truyền None vì không cần file thật
        new_user = dao.add_user(avatar_file=None, **user_data)

        # Kiểm tra xem người dùng đã được tạo và lưu vào DB chưa
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.username, 'newjobseeker')

        # Kiểm tra xem người dùng có thực sự trong DB không
        user_from_db = User.query.filter_by(username='newjobseeker').first()
        self.assertIsNotNone(user_from_db)
        self.assertEqual(user_from_db.email, 'new@jobseeker.com')


if __name__ == '__main__':
    unittest.main()