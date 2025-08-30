import unittest
import hashlib
from app import app, db
from app.models import User, RoleEnum, Job, JobStatusEnum, Company, Category
from app import dao


class TestIndexRoutes(unittest.TestCase):

    def setUp(self):
        """
        Set up the test environment before each test case.
        """
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for form testing

        self.client = app.test_client()

        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        # === START: ADD MORE SAMPLE DATA ===
        # 1. Create a job seeker user
        password = 'testpassword123'
        hashed_password = hashlib.md5(password.encode()).hexdigest()
        self.job_seeker_user = User(
            username='testuser',
            password=hashed_password,
            email='test@user.com',
            role=RoleEnum.JOBSEEKER
        )

        # 2. Create a recruiter user
        recruiter_password = 'recruiterpass'
        recruiter_hashed = hashlib.md5(recruiter_password.encode()).hexdigest()
        self.recruiter_user = User(
            username='testrecruiter',
            password=recruiter_hashed,
            email='recruiter@test.com',
            role=RoleEnum.RECRUITER
        )
        db.session.add_all([self.job_seeker_user, self.recruiter_user])
        db.session.commit()

        # 3. Create a company for the recruiter
        self.company = Company(user_id=self.recruiter_user.id, company_name='Test Company')
        db.session.add(self.company)
        db.session.commit()

        # 4. Create a category
        self.category = Category(name='IT')
        db.session.add(self.category)
        db.session.commit()

        # 5. Create a job that is 'POSTED'
        self.job = Job(
            title='Test Job',
            status=JobStatusEnum.POSTED,
            company_id=self.company.id,
            category_id=self.category.id
        )
        db.session.add(self.job)
        db.session.commit()
        # === END: ADD MORE SAMPLE DATA ===

    def tearDown(self):
        """
        Clean up the environment after each test case.
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_index_route(self):
        """Check if the homepage loads successfully."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # The database now has data, so these counts should render correctly.
        self.assertIn(b'Jobs Available', response.data)
        self.assertIn(b'Candidates', response.data)
        self.assertIn(b'Companies', response.data)

    def test_login_page_loads(self):
        """Check if the login page (GET) loads successfully."""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Account Login', response.data)

    def test_login_success(self):
        """Check for successful login (POST)."""
        response = self.client.post('/login', data=dict(
            username='testuser',
            password='testpassword123'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # After logging in and redirecting, the homepage should now show these texts
        self.assertIn(b'Jobs Available', response.data)
        self.assertIn(b'Logout', response.data)

    def test_login_fail_wrong_password(self):
        """Check for failed login (POST) due to wrong password."""
        response = self.client.post('/login', data=dict(
            username='testuser',
            password='wrongpassword'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Account Login', response.data)
        self.assertNotIn(b'Logout', response.data)

    def test_profile_access_unauthorized(self):
        """Check that accessing profile unauthorized returns a 401 error."""
        response = self.client.get('/profile', follow_redirects=False)

        assert response.status_code == 401

    def test_profile_access_authorized(self):
        """Check for successful access to the profile page after logging in."""
        self.client.post('/login', data=dict(
            username='testuser',
            password='testpassword123'
        ))
        response = self.client.get('/profile')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Resume & CV Management', response.data)


if __name__ == '__main__':
    unittest.main()