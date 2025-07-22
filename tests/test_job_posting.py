import unittest
from datetime import datetime, timedelta
from app import db, app
from app.models import Job, Company, Category, EmploymentEnum, JobStatusEnum, User, RoleEnum


class TestJobPosting(unittest.TestCase):
    def setUp(self):
        """Khởi tạo dữ liệu test"""
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Tạo user recruiter
        self.recruiter = User(
            username="test_recruiter",
            password="test_password",
            email="test@example.com",
            role=RoleEnum.RECRUITER
        )
        db.session.add(self.recruiter)
        db.session.commit()

        # Tạo company
        self.company = Company(
            user_id=self.recruiter.id,
            company_name="Test Company",
            website="http://test.com",
            industry="IT",
            company_size="50-100",
            address="Test Address"
        )
        db.session.add(self.company)

        # Tạo category
        self.category = Category(
            name="Test Category",
            description="Test Description"
        )
        db.session.add(self.category)
        db.session.commit()

        # Dữ liệu job hợp lệ
        self.valid_job_data = {
            'title': 'Software Engineer',
            'description': 'We are looking for a Python developer',
            'requirements': 'Python, Django, PostgreSQL',
            'location': 'Ha Noi, Vietnam',
            'salary': 1500.0,
            'employment_type': EmploymentEnum.FULLTIME,
            'expiration_date': datetime.now() + timedelta(days=30),
            'company_id': self.company.id,
            'category_id': self.category.id
        }

    def tearDown(self):
        """Dọn dẹp sau khi test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_job_posting(self):
        """Test tạo tin tuyển dụng với dữ liệu hợp lệ"""
        job = Job(**self.valid_job_data)
        db.session.add(job)
        db.session.commit()

        self.assertEqual(job.title, self.valid_job_data['title'])
        self.assertEqual(job.salary, self.valid_job_data['salary'])
        self.assertEqual(job.status, JobStatusEnum.DRAFT)

    def test_required_fields(self):
        """Test các trường bắt buộc"""
        invalid_data = self.valid_job_data.copy()
        del invalid_data['title']

        job = Job(**invalid_data)
        with self.assertRaises(Exception):
            db.session.add(job)
            db.session.commit()

    def test_job_status_transition(self):
        """Test chuyển trạng thái của job"""
        job = Job(**self.valid_job_data)
        db.session.add(job)
        db.session.commit()

        self.assertEqual(job.status, JobStatusEnum.DRAFT)

        job.status = JobStatusEnum.POSTED
        db.session.commit()
        self.assertEqual(job.status, JobStatusEnum.POSTED)

    def test_job_company_relationship(self):
        """Test mối quan hệ giữa Job và Company"""
        job = Job(**self.valid_job_data)
        db.session.add(job)
        db.session.commit()

        self.assertEqual(job.company.company_name, "Test Company")
        self.assertIn(job, self.company.jobs)

    def test_job_category_relationship(self):
        """Test mối quan hệ giữa Job và Category"""
        job = Job(**self.valid_job_data)
        db.session.add(job)
        db.session.commit()

        self.assertEqual(job.category.name, "Test Category")
        self.assertIn(job, self.category.jobs)


if __name__ == '__main__':
    unittest.main()