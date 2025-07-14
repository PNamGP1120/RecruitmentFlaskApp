# Trong tệp populate_db.py (hoặc nơi bạn có hàm populate_sample_data)

from app import db, app
from models import (
    User, Resume, Company, Category, Job, CV, Application,
    Interview, Conversation, Message, Notification,
    RoleEnum, EmploymentEnum, JobStatusEnum, ApplicationStatusEnum,
    conversation_user
)
from datetime import datetime, timedelta
import hashlib

def populate_sample_data():
    with app.app_context():
        print("--- Đang thêm dữ liệu mẫu ---")

        # Hàm trợ giúp để băm mật khẩu bằng MD5
        def hash_md5_password(password):
            return hashlib.md5(password.encode()).hexdigest()

        # --- Phần thêm Users, Companies, Resumes, Categories (giữ nguyên như trước) ---
        print("Đang thêm Users...")
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                password=hash_md5_password('admin123'),
                first_name='Admin',
                last_name='User',
                email='admin@example.com',
                role=RoleEnum.ADMIN,
                joined_date=datetime.now() - timedelta(days=365)
            )
            db.session.add(admin_user)

        recruiter_user = User.query.filter_by(username='recruiter1').first()
        if not recruiter_user:
            recruiter_user = User(
                username='recruiter1',
                password=hash_md5_password('recruiter123'),
                first_name='Nguyen',
                last_name='NhanSu',
                email='recruiter1@example.com',
                role=RoleEnum.RECRUITER,
                joined_date=datetime.now() - timedelta(days=180)
            )
            db.session.add(recruiter_user)

        jobseeker_user = User.query.filter_by(username='jobseeker1').first()
        if not jobseeker_user:
            jobseeker_user = User(
                username='jobseeker1',
                password=hash_md5_password('jobseeker123'),
                first_name='Tran',
                last_name='TimViec',
                email='jobseeker1@example.com',
                role=RoleEnum.JOBSEEKER,
                joined_date=datetime.now() - timedelta(days=90)
            )
            db.session.add(jobseeker_user)

        jobseeker_user2 = User.query.filter_by(username='jobseeker2').first()
        if not jobseeker_user2:
            jobseeker_user2 = User(
                username='jobseeker2',
                password=hash_md5_password('jobseeker234'),
                first_name='Le',
                last_name='ViecLam',
                email='jobseeker2@example.com',
                role=RoleEnum.JOBSEEKER,
                joined_date=datetime.now() - timedelta(days=60)
            )
            db.session.add(jobseeker_user2)
        db.session.commit()

        print("Đang thêm Companies...")
        company1 = Company.query.filter_by(company_name='FPT Software').first()
        if not company1:
            company1 = Company(
                user_id=recruiter_user.id,
                company_name='FPT Software',
                website='https://fptsoftware.com',
                introduction='Leading IT service provider in Vietnam.',
                industry='Software & IT',
                company_size='10000+',
                address='Ho Chi Minh City'
            )
            db.session.add(company1)

        company2 = Company.query.filter_by(company_name='VinGroup').first()
        if not company2:
            company2 = Company(
                user_id=recruiter_user.id,
                company_name='VinGroup',
                website='https://vingroup.net',
                introduction='Diversified conglomerate in Vietnam.',
                industry='Diversified',
                company_size='50000+',
                address='Hanoi'
            )
            db.session.add(company2)
        db.session.commit()

        print("Đang thêm Resumes...")
        resume1 = Resume.query.filter_by(user_id=jobseeker_user.id).first()
        if not resume1:
            resume1 = Resume(
                user_id=jobseeker_user.id,
                skill='Python, Flask, SQLAlchemy, JavaScript, React',
                experience='3 years as Software Developer',
                education='Bachelor of Computer Science',
                preferred_locations='Ho Chi Minh City, Ha Noi',
                preferred_job_types='Fulltime',
                linkedin_url='https://linkedin.com/in/tran-timviec'
            )
            db.session.add(resume1)

        resume2 = Resume.query.filter_by(user_id=jobseeker_user2.id).first()
        if not resume2:
            resume2 = Resume(
                user_id=jobseeker_user2.id,
                skill='Java, Spring Boot, SQL, AWS',
                experience='5 years as Senior Software Engineer',
                education='Master of Software Engineering',
                preferred_locations='Ha Noi',
                preferred_job_types='Fulltime',
                linkedin_url='https://linkedin.com/in/le-vieclam'
            )
            db.session.add(resume2)
        db.session.commit()

        print("Đang thêm Categories...")
        it_category = Category.query.filter_by(name='IT - Software').first()
        if not it_category:
            it_category = Category(name='IT - Software', description='Information Technology and Software Development.')
            db.session.add(it_category)

        marketing_category = Category.query.filter_by(name='Marketing').first()
        if not marketing_category:
            marketing_category = Category(name='Marketing', description='Marketing and Communications roles.')
            db.session.add(marketing_category)

        finance_category = Category.query.filter_by(name='Finance').first()
        if not finance_category:
            finance_category = Category(name='Finance', description='Finance and Accounting positions.')
            db.session.add(finance_category)

        design_category = Category.query.filter_by(name='Design').first()
        if not design_category:
            design_category = Category(name='Design', description='Graphic Design, UX/UI Design roles.')
            db.session.add(design_category)

        hr_category = Category.query.filter_by(name='Human Resources').first()
        if not hr_category:
            hr_category = Category(name='Human Resources', description='HR and Recruitment roles.')
            db.session.add(hr_category)

        db.session.commit()

        # --- Phần thêm Jobs (đã có) ---
        print("Đang thêm Jobs (đã có)...")
        job_python = Job.query.filter_by(title='Python Developer').first()
        if not job_python:
            job_python = Job(
                title='Python Developer',
                description='We are looking for a skilled Python Developer to join our team.',
                requirements='Experience with Flask/Django, REST APIs, PostgreSQL.',
                location='Ho Chi Minh City',
                salary=1500.00,
                employment_type=EmploymentEnum.FULLTIME,
                status=JobStatusEnum.POSTED,
                expiration_date=datetime.now() + timedelta(days=30),
                created_date=datetime.now() - timedelta(days=10),
                company_id=company1.id,
                category_id=it_category.id,
                view_count=150
            )
            db.session.add(job_python)

        job_frontend = Job.query.filter_by(title='Frontend Developer (ReactJS)').first()
        if not job_frontend:
            job_frontend = Job(
                title='Frontend Developer (ReactJS)',
                description='Join our dynamic frontend team, focusing on ReactJS.',
                requirements='Strong knowledge of HTML, CSS, JavaScript, ReactJS.',
                location='Ho Chi Minh City',
                salary=1200.00,
                employment_type=EmploymentEnum.FULLTIME,
                status=JobStatusEnum.POSTED,
                expiration_date=datetime.now() + timedelta(days=20),
                created_date=datetime.now() - timedelta(days=7),
                company_id=company1.id,
                category_id=it_category.id,
                view_count=200
            )
            db.session.add(job_frontend)

        job_data_analyst = Job.query.filter_by(title='Data Analyst').first()
        if not job_data_analyst:
            job_data_analyst = Job(
                title='Data Analyst',
                description='Analyze complex data sets to provide actionable insights.',
                requirements='Proficiency in SQL, Excel, Python/R, data visualization tools.',
                location='Ha Noi',
                salary=1000.00,
                employment_type=EmploymentEnum.FULLTIME,
                status=JobStatusEnum.POSTED,
                expiration_date=datetime.now() + timedelta(days=25),
                created_date=datetime.now() - timedelta(days=15),
                company_id=company1.id,
                category_id=it_category.id,
                view_count=180
            )
            db.session.add(job_data_analyst)

        job_marketing_intern = Job.query.filter_by(title='Marketing Intern').first()
        if not job_marketing_intern:
            job_marketing_intern = Job(
                title='Marketing Intern',
                description='Support marketing campaigns and content creation.',
                requirements='Basic understanding of digital marketing, good communication.',
                location='Ha Noi',
                salary=300.00,
                employment_type=EmploymentEnum.PARTTIME,
                status=JobStatusEnum.POSTED,
                expiration_date=datetime.now() + timedelta(days=40),
                created_date=datetime.now() - timedelta(days=5),
                company_id=company2.id,
                category_id=marketing_category.id,
                view_count=80
            )
            db.session.add(job_marketing_intern)

        job_hr_specialist = Job.query.filter_by(title='HR Specialist (Draft)').first()
        if not job_hr_specialist:
            job_hr_specialist = Job(
                title='HR Specialist (Draft)',
                description='Manage HR operations and employee relations.',
                requirements='Experience in HR, good communication and problem-solving skills.',
                location='Ho Chi Minh City',
                salary=800.00,
                employment_type=EmploymentEnum.FULLTIME,
                status=JobStatusEnum.DRAFT,
                expiration_date=datetime.now() + timedelta(days=90),
                created_date=datetime.now() - timedelta(days=2),
                company_id=company1.id,
                category_id=hr_category.id, # Sử dụng category HR mới
                view_count=10
            )
            db.session.add(job_hr_specialist)
        db.session.commit()

        # --- Thêm 10 công việc mới ---
        print("Đang thêm 10 công việc mới...")

        new_jobs_data = [
            {
                'title': 'Senior Java Developer',
                'description': 'Develop and maintain high-performance Java applications.',
                'requirements': '5+ years Java, Spring Boot, Microservices.',
                'location': 'Ha Noi',
                'salary': 2000.00,
                'employment_type': EmploymentEnum.FULLTIME,
                'company': company1,
                'category': it_category
            },
            {
                'title': 'UX/UI Designer',
                'description': 'Design intuitive and engaging user interfaces.',
                'requirements': 'Proficiency in Figma, Sketch, Adobe XD. Portfolio required.',
                'location': 'Ho Chi Minh City',
                'salary': 900.00,
                'employment_type': EmploymentEnum.FULLTIME,
                'company': company2,
                'category': design_category
            },
            {
                'title': 'Content Marketing Specialist',
                'description': 'Create compelling content for various marketing channels.',
                'requirements': 'Excellent writing skills, SEO knowledge.',
                'location': 'Ha Noi',
                'salary': 700.00,
                'employment_type': EmploymentEnum.FULLTIME,
                'company': company2,
                'category': marketing_category
            },
            {
                'title': 'Financial Analyst',
                'description': 'Conduct financial modeling and analysis.',
                'requirements': 'CFA or equivalent, strong analytical skills.',
                'location': 'Ho Chi Minh City',
                'salary': 1800.00,
                'employment_type': EmploymentEnum.FULLTIME,
                'company': company1,
                'category': finance_category
            },
            {
                'title': 'Mobile App Developer (iOS/Android)',
                'description': 'Develop cross-platform mobile applications.',
                'requirements': 'Experience with React Native or Flutter.',
                'location': 'Da Nang',
                'salary': 1400.00,
                'employment_type': EmploymentEnum.FULLTIME,
                'company': company1,
                'category': it_category
            },
            {
                'title': 'Part-time Customer Support',
                'description': 'Provide excellent customer service and support.',
                'requirements': 'Good communication, problem-solving skills.',
                'location': 'Ho Chi Minh City',
                'salary': 400.00,
                'employment_type': EmploymentEnum.PARTTIME,
                'company': company2,
                'category': None # Có thể không có category cụ thể
            },
            {
                'title': 'DevOps Engineer',
                'description': 'Build and maintain our CI/CD pipelines and infrastructure.',
                'requirements': 'AWS, Docker, Kubernetes, Jenkins.',
                'location': 'Ha Noi',
                'salary': 1700.00,
                'employment_type': EmploymentEnum.FULLTIME,
                'company': company1,
                'category': it_category
            },
            {
                'title': 'Business Development Executive',
                'description': 'Identify new business opportunities and partnerships.',
                'requirements': 'Proven sales track record, strong negotiation skills.',
                'location': 'Ho Chi Minh City',
                'salary': 1600.00,
                'employment_type': EmploymentEnum.FULLTIME,
                'company': company2,
                'category': None
            },
            {
                'title': 'Junior QA Engineer',
                'description': 'Test software applications to ensure quality.',
                'requirements': 'Basic testing knowledge, attention to detail.',
                'location': 'Ha Noi',
                'salary': 700.00,
                'employment_type': EmploymentEnum.FULLTIME,
                'company': company1,
                'category': it_category
            },
            {
                'title': 'HR Assistant',
                'description': 'Support HR department with administrative tasks.',
                'requirements': 'Organizational skills, basic HR knowledge.',
                'location': 'Ho Chi Minh City',
                'salary': 500.00,
                'employment_type': EmploymentEnum.PARTTIME,
                'company': company2,
                'category': hr_category
            }
        ]

        for i, job_data in enumerate(new_jobs_data):
            # Tạo tên job duy nhất để tránh trùng lặp khi chạy lại script
            job_title = job_data['title']
            existing_job = Job.query.filter_by(title=job_title).first()
            if not existing_job:
                new_job = Job(
                    title=job_title,
                    description=job_data['description'],
                    requirements=job_data['requirements'],
                    location=job_data['location'],
                    salary=job_data['salary'],
                    employment_type=job_data['employment_type'],
                    status=JobStatusEnum.POSTED, # Mặc định là Posted
                    expiration_date=datetime.now() + timedelta(days=30 + i*2), # Ngày hết hạn khác nhau
                    created_date=datetime.now() - timedelta(days=i), # Ngày tạo khác nhau
                    company_id=job_data['company'].id,
                    category_id=job_data['category'].id if job_data['category'] else None,
                    view_count=50 + i*10
                )
                db.session.add(new_job)
                print(f"Đã thêm Job: {new_job.title}")
            else:
                print(f"Job '{job_title}' đã tồn tại, bỏ qua.")
        db.session.commit() # Commit tất cả các job mới

        # --- Các phần thêm CVs, Applications, Interviews, Conversations, Messages, Notifications (giữ nguyên) ---
        print("Đang thêm CVs...")
        cv_js1_python = CV.query.filter_by(resume_id=resume1.id, title='Python Dev CV').first()
        if not cv_js1_python:
            cv_js1_python = CV(
                resume_id=resume1.id,
                title='Python Dev CV',
                file_path='/static/cvs/tran_timviec_python.pdf',
                is_default=True,
                created_date=datetime.now() - timedelta(days=80)
            )
            db.session.add(cv_js1_python)

        cv_js2_java = CV.query.filter_by(resume_id=resume2.id, title='Java Engineer CV').first()
        if not cv_js2_java:
            cv_js2_java = CV(
                resume_id=resume2.id,
                title='Java Engineer CV',
                file_path='/static/cvs/le_vieclam_java.pdf',
                is_default=True,
                created_date=datetime.now() - timedelta(days=50)
            )
            db.session.add(cv_js2_java)
        db.session.commit()

        print("Đang thêm Applications...")
        app_js1_python_job = Application.query.filter_by(cv_id=cv_js1_python.id, job_id=job_python.id).first()
        if not app_js1_python_job:
            app_js1_python_job = Application(
                cv_id=cv_js1_python.id,
                job_id=job_python.id,
                cover_letter='Looking forward to contributing my Python skills.',
                status=ApplicationStatusEnum.PENDING,
                applied_date=datetime.now() - timedelta(days=5)
            )
            db.session.add(app_js1_python_job)

        app_js1_frontend_job = Application.query.filter_by(cv_id=cv_js1_python.id, job_id=job_frontend.id).first()
        if not app_js1_frontend_job:
            app_js1_frontend_job = Application(
                cv_id=cv_js1_python.id,
                job_id=job_frontend.id,
                cover_letter='Excited about ReactJS opportunities.',
                status=ApplicationStatusEnum.CONFIRMED,
                applied_date=datetime.now() - timedelta(days=3),
                updated_date=datetime.now() - timedelta(days=1),
                feedback='Initial review positive. Proceeding to interview.'
            )
            db.session.add(app_js1_frontend_job)

        app_js2_data_analyst_job = Application.query.filter_by(cv_id=cv_js2_java.id, job_id=job_data_analyst.id).first()
        if not app_js2_data_analyst_job:
            app_js2_data_analyst_job = Application(
                cv_id=cv_js2_java.id,
                job_id=job_data_analyst.id,
                cover_letter='Experienced in data analysis and ready for new challenges.',
                status=ApplicationStatusEnum.ACCEPTED,
                applied_date=datetime.now() - timedelta(days=10),
                updated_date=datetime.now() - timedelta(days=2),
                feedback='Candidate accepted offer.'
            )
            db.session.add(app_js2_data_analyst_job)
        db.session.commit()

        print("Đang thêm Interviews...")
        interview1 = Interview.query.filter_by(application_id=app_js1_frontend_job.id).first()
        if not interview1:
            interview1 = Interview(
                application_id=app_js1_frontend_job.id,
                dateTime=datetime.now() + timedelta(days=2),
                url='https://zoom.us/j/1234567890'
            )
            db.session.add(interview1)
        db.session.commit()

        print("Đang thêm Conversations và Messages...")
        conv1 = Conversation.query.filter_by(id=1).first()
        if not conv1:
            conv1 = Conversation(created_date=datetime.now() - timedelta(minutes=60))
            db.session.add(conv1)
            db.session.commit()

            conv1.users.append(recruiter_user)
            conv1.users.append(jobseeker_user)
            db.session.commit()

        msg1 = Message.query.filter_by(conversation_id=conv1.id, sender_id=recruiter_user.id).first()
        if not msg1:
            msg1 = Message(
                conversation_id=conv1.id,
                sender_id=recruiter_user.id,
                content='Hi Tran, we reviewed your application for Python Developer. When are you available for an interview?',
                timestamp=datetime.now() - timedelta(minutes=50),
                is_read=False
            )
            db.session.add(msg1)

        msg2 = Message.query.filter_by(conversation_id=conv1.id, sender_id=jobseeker_user.id).first()
        if not msg2:
            msg2 = Message(
                conversation_id=conv1.id,
                sender_id=jobseeker_user.id,
                content='Hi! I am available on Tuesday afternoon. Does that work?',
                timestamp=datetime.now() - timedelta(minutes=40),
                is_read=True
            )
            db.session.add(msg2)
        db.session.commit()

        print("Đang thêm Notifications...")
        notif1 = Notification.query.filter_by(user_id=jobseeker_user.id, content='Your application for Frontend Developer has been confirmed.').first()
        if not notif1:
            notif1 = Notification(
                user_id=jobseeker_user.id,
                content='Your application for Frontend Developer has been confirmed.',
                is_read=False,
                created_date=datetime.now() - timedelta(minutes=30)
            )
            db.session.add(notif1)

        notif2 = Notification.query.filter_by(user_id=recruiter_user.id, content='New application for Python Developer.').first()
        if not notif2:
            notif2 = Notification(
                user_id=recruiter_user.id,
                content='New application for Python Developer.',
                is_read=False,
                created_date=datetime.now() - timedelta(minutes=25)
            )
            db.session.add(notif2)
        db.session.commit()

        print("--- Hoàn thành thêm dữ liệu mẫu! ---")

if __name__ == '__main__':
    populate_sample_data()