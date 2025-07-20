# populate_db.py

import hashlib
from datetime import datetime, timedelta
from app import db, app
from models import ( # Import tất cả các model và Enum cần thiết
    User, Resume, Company, Category, Job, CV, Application,
    Interview, Conversation, Message, Notification,
    RoleEnum, EmploymentEnum, JobStatusEnum, ApplicationStatusEnum
)
from sqlalchemy.orm.exc import NoResultFound

def hash_md5_password(password):
    """Băm mật khẩu bằng MD5."""
    return hashlib.md5(password.encode()).hexdigest()

def get_or_create(session, model, **kwargs):
    """
    Hàm tiện ích để tìm một đối tượng trong DB, nếu không có thì tạo mới.
    Sử dụng session được truyền vào để đảm bảo tính nhất quán.
    """
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        # print(f"Đã tồn tại {model.__name__}: {kwargs}") # Có thể bỏ comment để debug
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        print(f"Đã tạo mới {model.__name__}: {kwargs}")
        return instance

def populate_sample_data():
    with app.app_context():
        # Sử dụng db.session để tương tác với database
        session = db.session
        print("--- Đang bắt đầu chèn dữ liệu mẫu ---")

        # --- 1. Users ---
        print("\n--- 1. Thêm Users ---")
        admin_user = get_or_create(session, User,
            username='admin',
            password=hash_md5_password('admin123'),
            first_name='Admin',
            last_name='User',
            email='admin@example.com',
            role=RoleEnum.ADMIN,
            joined_date=datetime.now() - timedelta(days=365)
        )

        recruiter_user1 = get_or_create(session, User,
            username='recruiter1',
            password=hash_md5_password('recruiter123'),
            first_name='Nguyen',
            last_name='NhanSu',
            email='recruiter1@example.com',
            role=RoleEnum.RECRUITER,
            joined_date=datetime.now() - timedelta(days=180)
        )

        recruiter_user2 = get_or_create(session, User,
            username='recruiter2',
            password=hash_md5_password('recruiter456'),
            first_name='Pham',
            last_name='Tuyendung',
            email='recruiter2@example.com',
            role=RoleEnum.RECRUITER,
            joined_date=datetime.now() - timedelta(days=120)
        )

        jobseeker_user1 = get_or_create(session, User,
            username='jobseeker1',
            password=hash_md5_password('jobseeker123'),
            first_name='Tran',
            last_name='TimViec',
            email='jobseeker1@example.com',
            role=RoleEnum.JOBSEEKER,
            joined_date=datetime.now() - timedelta(days=90)
        )

        jobseeker_user2 = get_or_create(session, User,
            username='jobseeker2',
            password=hash_md5_password('jobseeker234'),
            first_name='Le',
            last_name='ViecLam',
            email='jobseeker2@example.com',
            role=RoleEnum.JOBSEEKER,
            joined_date=datetime.now() - timedelta(days=60)
        )
        session.commit() # Commit users để có ID trước khi dùng cho Companies/Resumes

        # --- 2. Companies ---
        print("\n--- 2. Thêm Companies ---")
        company1 = get_or_create(session, Company,
            user_id=recruiter_user1.id,
            company_name='FPT Software',
            website='https://fptsoftware.com',
            introduction='Leading IT service provider in Vietnam, specializing in digital transformation.',
            industry='Software & IT Services',
            company_size='10000+',
            address='Ho Chi Minh City, Vietnam'
        )

        company2 = get_or_create(session, Company,
            user_id=recruiter_user2.id,
            company_name='VinGroup',
            website='https://vingroup.net',
            introduction='Vietnam\'s largest diversified conglomerate, with interests in real estate, automotive, and technology.',
            industry='Diversified Conglomerate',
            company_size='50000+',
            address='Hanoi, Vietnam'
        )
        session.commit() # Commit companies để có ID trước khi dùng cho Jobs

        # --- 3. Resumes ---
        print("\n--- 3. Thêm Resumes ---")
        resume1 = get_or_create(session, Resume,
            user_id=jobseeker_user1.id,
            skill='Python, Flask, SQLAlchemy, JavaScript, React, REST APIs, PostgreSQL',
            experience='3 years as Software Developer at Tech Solutions Inc., specializing in web applications.',
            education='Bachelor of Computer Science, University of Technology (2020)',
            preferred_locations='Ho Chi Minh City, Ha Noi',
            preferred_job_types='Fulltime',
            linkedin_url='https://linkedin.com/in/tran-timviec-dev'
        )

        resume2 = get_or_create(session, Resume,
            user_id=jobseeker_user2.id,
            skill='Java, Spring Boot, SQL, AWS, Microservices, Docker, Kubernetes',
            experience='5 years as Senior Software Engineer at Global Tech Corp, leading backend development teams.',
            education='Master of Software Engineering, National University (2018)',
            preferred_locations='Ha Noi, Da Nang',
            preferred_job_types='Fulltime',
            linkedin_url='https://linkedin.com/in/le-vieclam-eng'
        )
        session.commit() # Commit resumes

        # --- 4. Categories ---
        print("\n--- 4. Thêm Categories ---")
        it_category = get_or_create(session, Category, name='IT - Software', description='Information Technology and Software Development.')
        marketing_category = get_or_create(session, Category, name='Marketing', description='Marketing and Communications roles.')
        finance_category = get_or_create(session, Category, name='Finance', description='Finance and Accounting positions.')
        design_category = get_or_create(session, Category, name='Design', description='Graphic Design, UX/UI Design roles.')
        hr_category = get_or_create(session, Category, name='Human Resources', description='HR and Recruitment roles.')
        engineering_category = get_or_create(session, Category, name='Engineering', description='Various engineering disciplines (e.g., Civil, Mechanical).')
        session.commit() # Commit categories

        # --- 5. Jobs ---
        print("\n--- 5. Thêm Jobs ---")
        jobs_data = [
            {
                'title': 'Python Developer', 'description': 'We are looking for a skilled Python Developer to join our team, focusing on backend services and API development for our core products.',
                'requirements': '3+ years experience with Python, Flask/Django, REST APIs, PostgreSQL. Knowledge of cloud platforms (AWS/GCP) is a plus. Strong problem-solving skills.', 'location': 'Ho Chi Minh City',
                'salary': 1500.00, 'employment_type': EmploymentEnum.FULLTIME, 'status': JobStatusEnum.POSTED,
                'expiration_offset': 30, 'created_offset': 10, 'company': company1, 'category': it_category, 'view_count': 150
            },
            {
                'title': 'Frontend Developer (ReactJS)', 'description': 'Join our dynamic frontend team, focusing on building responsive and intuitive user interfaces using ReactJS for our consumer-facing applications.',
                'requirements': 'Strong knowledge of HTML5, CSS3, JavaScript (ES6+), ReactJS, Redux, Webpack. Familiarity with UI/UX principles and version control (Git).', 'location': 'Ho Chi Minh City',
                'salary': 1200.00, 'employment_type': EmploymentEnum.FULLTIME, 'status': JobStatusEnum.POSTED,
                'expiration_offset': 20, 'created_offset': 7, 'company': company1, 'category': it_category, 'view_count': 200
            },
            {
                'title': 'Data Analyst', 'description': 'Analyze complex data sets to provide actionable insights and support business decision-making across various departments.',
                'requirements': 'Proficiency in SQL, Excel, Python/R for data manipulation and analysis. Experience with data visualization tools like Tableau/Power BI. Strong communication skills.', 'location': 'Ha Noi',
                'salary': 1000.00, 'employment_type': EmploymentEnum.FULLTIME, 'status': JobStatusEnum.POSTED,
                'expiration_offset': 25, 'created_offset': 15, 'company': company1, 'category': it_category, 'view_count': 180
            },
            {
                'title': 'Marketing Intern', 'description': 'Support marketing campaigns, content creation, and social media management for our diverse brands.',
                'requirements': 'Basic understanding of digital marketing principles. Excellent written and verbal communication skills in Vietnamese and English. Eagerness to learn and proactive attitude.', 'location': 'Ha Noi',
                'salary': 300.00, 'employment_type': EmploymentEnum.PARTTIME, 'status': JobStatusEnum.POSTED,
                'expiration_offset': 40, 'created_offset': 5, 'company': company2, 'category': marketing_category, 'view_count': 80
            },
            {
                'title': 'HR Specialist (Draft)', 'description': 'Manage HR operations, employee relations, and recruitment support for various business units.',
                'requirements': '2+ years experience in HR, preferably in a fast-paced environment. Strong communication, interpersonal, and problem-solving skills. Knowledge of labor laws.', 'location': 'Ho Chi Minh City',
                'salary': 800.00, 'employment_type': EmploymentEnum.FULLTIME, 'status': JobStatusEnum.DRAFT,
                'expiration_offset': 90, 'created_offset': 2, 'company': company1, 'category': hr_category, 'view_count': 10
            },
            {
                'title': 'Senior Java Developer', 'description': 'Develop and maintain high-performance Java applications, focusing on scalable backend systems and distributed architectures.',
                'requirements': '5+ years experience in Java, Spring Boot, Microservices architecture. Experience with cloud platforms like AWS or Azure. Strong understanding of design patterns.', 'location': 'Ha Noi',
                'salary': 2000.00, 'employment_type': EmploymentEnum.FULLTIME, 'status': JobStatusEnum.POSTED,
                'expiration_offset': 35, 'created_offset': 12, 'company': company1, 'category': it_category, 'view_count': 250
            },
            {
                'title': 'UX/UI Designer', 'description': 'Design intuitive and engaging user interfaces and experiences for our web and mobile products, collaborating closely with product and engineering teams.',
                'requirements': 'Proficiency in Figma, Sketch, Adobe XD. Strong portfolio showcasing user-centered design principles, wireframing, and prototyping skills.', 'location': 'Ho Chi Minh City',
                'salary': 900.00, 'employment_type': EmploymentEnum.FULLTIME, 'status': JobStatusEnum.POSTED,
                'expiration_offset': 28, 'created_offset': 9, 'company': company2, 'category': design_category, 'view_count': 120
            },
            {
                'title': 'Content Marketing Specialist', 'description': 'Develop and execute content strategies to drive brand awareness, engagement, and lead generation across various digital channels.',
                'requirements': 'Excellent writing and editing skills. Proven experience in SEO, content creation (blogs, articles, video scripts), and social media marketing. Creative mindset.', 'location': 'Ha Noi',
                'salary': 700.00, 'employment_type': EmploymentEnum.FULLTIME, 'status': JobStatusEnum.POSTED,
                'expiration_offset': 45, 'created_offset': 10, 'company': company2, 'category': marketing_category, 'view_count': 90
            },
            {
                'title': 'Financial Analyst', 'description': 'Conduct financial modeling, forecasting, and performance analysis to support strategic decisions and investment opportunities.',
                'requirements': 'CFA or equivalent preferred. Strong analytical skills, attention to detail, and proficiency in financial software (e.g., SAP, Oracle Financials).', 'location': 'Ho Chi Minh City',
                'salary': 1800.00, 'employment_type': EmploymentEnum.FULLTIME, 'status': JobStatusEnum.POSTED,
                'expiration_offset': 32, 'created_offset': 18, 'company': company1, 'category': finance_category, 'view_count': 160
            },
            {
                'title': 'Mobile App Developer (iOS/Android)', 'description': 'Develop and maintain high-performance, cross-platform mobile applications for iOS and Android, ensuring seamless user experience.',
                'requirements': 'Experience with React Native or Flutter. Strong understanding of mobile UI/UX best practices, API integration, and performance optimization.', 'location': 'Da Nang',
                'salary': 1400.00, 'employment_type': EmploymentEnum.FULLTIME, 'status': JobStatusEnum.POSTED,
                'expiration_offset': 22, 'created_offset': 6, 'company': company1, 'category': it_category, 'view_count': 210
            },
             {
                'title': 'Part-time Customer Support', 'description': 'Provide excellent customer service and technical support to our users via chat, email, and phone.',
                'requirements': 'Strong communication and problem-solving skills. Ability to work flexible hours and handle challenging customer interactions professionally.', 'location': 'Ho Chi Minh City',
                'salary': 400.00, 'employment_type': EmploymentEnum.PARTTIME, 'status': JobStatusEnum.POSTED,
                'expiration_offset': 50, 'created_offset': 3, 'company': company2, 'category': None, 'view_count': 60
            },
            {
                'title': 'DevOps Engineer', 'description': 'Build and maintain our CI/CD pipelines, automate infrastructure, and ensure system reliability and scalability.',
                'requirements': 'Proficiency in AWS, Docker, Kubernetes, Jenkins, Git. Experience with infrastructure as code (Terraform) and monitoring tools (Prometheus).', 'location': 'Ha Noi',
                'salary': 1700.00, 'employment_type': EmploymentEnum.FULLTIME, 'status': JobStatusEnum.POSTED,
                'expiration_offset': 27, 'created_offset': 14, 'company': company1, 'category': it_category, 'view_count': 190
            },
            {
                'title': 'Business Development Executive', 'description': 'Identify new business opportunities, build strong client relationships, and drive revenue growth in target markets.',
                'requirements': 'Proven sales track record, strong negotiation and presentation skills. Ability to work independently and as part of a team. Excellent communication.', 'location': 'Ho Chi Minh City',
                'salary': 1600.00, 'employment_type': EmploymentEnum.FULLTIME, 'status': JobStatusEnum.POSTED,
                'expiration_offset': 38, 'created_offset': 8, 'company': company2, 'category': None, 'view_count': 110
            },
            {
                'title': 'Junior QA Engineer', 'description': 'Perform manual and automated testing of software applications to ensure quality and identify bugs before release.',
                'requirements': 'Basic understanding of software testing methodologies. Attention to detail and good communication skills. Familiarity with test case management tools.', 'location': 'Ha Noi',
                'salary': 700.00, 'employment_type': EmploymentEnum.FULLTIME, 'status': JobStatusEnum.POSTED,
                'expiration_offset': 20, 'created_offset': 4, 'company': company1, 'category': it_category, 'view_count': 100
            },
            {
                'title': 'HR Assistant', 'description': 'Support the HR department with administrative tasks, employee onboarding, record keeping, and basic HR inquiries.',
                'requirements': 'Strong organizational skills, attention to detail, and basic knowledge of HR processes. Proficiency in MS Office Suite. Discretion and confidentiality.', 'location': 'Ho Chi Minh City',
                'salary': 500.00, 'employment_type': EmploymentEnum.PARTTIME, 'status': JobStatusEnum.POSTED,
                'expiration_offset': 60, 'created_offset': 2, 'company': company2, 'category': hr_category, 'view_count': 70
            }
        ]

        for job_data in jobs_data:
            get_or_create(session, Job,
                title=job_data['title'],
                company_id=job_data['company'].id, # Sử dụng ID của Company đã tồn tại
                description=job_data['description'],
                requirements=job_data['requirements'],
                location=job_data['location'],
                salary=job_data['salary'],
                employment_type=job_data['employment_type'],
                status=job_data['status'],
                expiration_date=datetime.now() + timedelta(days=job_data['expiration_offset']),
                created_date=datetime.now() - timedelta(days=job_data['created_offset']),
                category_id=job_data['category'].id if job_data['category'] else None,
                view_count=job_data['view_count']
            )
        session.commit() # Commit tất cả jobs

        # Lấy lại các Job đã được thêm để đảm bảo ID chính xác khi dùng cho Applications
        job_python = Job.query.filter_by(title='Python Developer', company_id=company1.id).first()
        job_frontend = Job.query.filter_by(title='Frontend Developer (ReactJS)', company_id=company1.id).first()
        job_data_analyst = Job.query.filter_by(title='Data Analyst', company_id=company1.id).first()
        job_senior_java = Job.query.filter_by(title='Senior Java Developer', company_id=company1.id).first()
        job_ux_ui = Job.query.filter_by(title='UX/UI Designer', company_id=company2.id).first()
        job_junior_qa = Job.query.filter_by(title='Junior QA Engineer', company_id=company1.id).first()
        job_mobile_dev = Job.query.filter_by(title='Mobile App Developer (iOS/Android)', company_id=company1.id).first()
        job_content_marketing = Job.query.filter_by(title='Content Marketing Specialist', company_id=company2.id).first()


        # --- 6. CVs ---
        print("\n--- 6. Thêm CVs ---")
        cv_js1_python = get_or_create(session, CV,
            resume_id=resume1.id,
            title='Python Dev CV - Tran TimViec',
            file_path='/static/profile/tran_timviec_python_cv.pdf',
            is_default=True,
            created_date=datetime.now() - timedelta(days=80)
        )

        cv_js1_fe = get_or_create(session, CV,
            resume_id=resume1.id,
            title='Frontend Dev CV - Tran TimViec',
            file_path='/static/profile/tran_timviec_frontend_cv.pdf',
            is_default=False,
            created_date=datetime.now() - timedelta(days=70)
        )

        cv_js2_java = get_or_create(session, CV,
            resume_id=resume2.id,
            title='Java Engineer CV - Le ViecLam',
            file_path='/static/profile/le_vieclam_java_cv.pdf',
            is_default=True,
            created_date=datetime.now() - timedelta(days=50)
        )
        session.commit() # Commit CVs

        # --- 7. Applications ---
        print("\n--- 7. Thêm Applications ---")
        # Application 1: jobseeker1 applies for Python Developer (PENDING)
        if job_python and cv_js1_python:
            get_or_create(session, Application,
                job_id=job_python.id,
                cv_id=cv_js1_python.id,
                cover_letter='Looking forward to contributing my Python skills to your esteemed company. I have extensive experience in backend development.',
                status=ApplicationStatusEnum.PENDING,
                applied_date=datetime.now() - timedelta(days=5)
            )

        # Application 2: jobseeker1 applies for Frontend Developer (CONFIRMED)
        if job_frontend and cv_js1_fe:
            app2 = get_or_create(session, Application,
                job_id=job_frontend.id,
                cv_id=cv_js1_fe.id,
                cover_letter='Excited about ReactJS opportunities and confident in my frontend abilities. My portfolio showcases various React projects.',
                status=ApplicationStatusEnum.CONFIRMED,
                applied_date=datetime.now() - timedelta(days=3),
                updated_date=datetime.now() - timedelta(days=1),
                feedback='Initial review positive. Proceeding to interview. Strong React portfolio.'
            )

        # Application 3: jobseeker2 applies for Data Analyst (ACCEPTED)
        if job_data_analyst and cv_js2_java:
            get_or_create(session, Application,
                job_id=job_data_analyst.id,
                cv_id=cv_js2_java.id, # Dù CV là Java, nhưng vẫn có thể ứng tuyển Data Analyst nếu kỹ năng phù hợp
                cover_letter='Experienced in data analysis and ready for new challenges in your data team. Proficient in SQL and Python for data manipulation.',
                status=ApplicationStatusEnum.ACCEPTED,
                applied_date=datetime.now() - timedelta(days=10),
                updated_date=datetime.now() - timedelta(days=2),
                feedback='Candidate accepted offer. Excellent fit for the role.'
            )

        # Application 4: jobseeker1 applies for Senior Java Developer (REJECTED)
        if job_senior_java and cv_js1_python:
            get_or_create(session, Application,
                job_id=job_senior_java.id,
                cv_id=cv_js1_python.id, # Có thể dùng CV Python cho Java, tùy vào ứng viên
                cover_letter='Interested in the Senior Java role, though my primary expertise is Python. Willing to learn and adapt to new technologies.',
                status=ApplicationStatusEnum.REJECTED,
                applied_date=datetime.now() - timedelta(days=7),
                updated_date=datetime.now() - timedelta(days=4),
                feedback='Skills mismatch for Java role. Strong Python but not enough Java experience.'
            )

        # Application 5: jobseeker2 applies for UX/UI Designer (PENDING)
        if job_ux_ui and cv_js2_java: # Giả sử jobseeker2 cũng có thể có một CV cho Design nếu cần
            get_or_create(session, Application,
                job_id=job_ux_ui.id,
                cv_id=cv_js2_java.id, # Sử dụng CV Java của js2 (có thể không lý tưởng nhưng là ví dụ)
                cover_letter='My passion for user experience drives me to apply for this UX/UI role. I have strong design principles.',
                status=ApplicationStatusEnum.PENDING,
                applied_date=datetime.now() - timedelta(days=1)
            )

        # Application 6: jobseeker2 applies for Junior QA Engineer (DRAFT) - Example of draft status
        if job_junior_qa and cv_js2_java:
            get_or_create(session, Application,
                job_id=job_junior_qa.id,
                cv_id=cv_js2_java.id,
                cover_letter='Starting draft for QA position. Will finalize soon.',
                status=ApplicationStatusEnum.DRAFT,
                applied_date=datetime.now() - timedelta(hours=12) # Mới tạo
            )

        # Application 7: jobseeker1 applies for Mobile App Developer (PENDING)
        if job_mobile_dev and cv_js1_fe:
            get_or_create(session, Application,
                job_id=job_mobile_dev.id,
                cv_id=cv_js1_fe.id,
                cover_letter='My frontend skills align well with mobile app development using React Native.',
                status=ApplicationStatusEnum.PENDING,
                applied_date=datetime.now() - timedelta(days=2)
            )

        # Application 8: jobseeker2 applies for Content Marketing (PENDING)
        if job_content_marketing and cv_js2_java: # Sử dụng CV Java của js2, giả sử CV này đa năng
            get_or_create(session, Application,
                job_id=job_content_marketing.id,
                cv_id=cv_js2_java.id,
                cover_letter='Eager to leverage my communication skills in a content marketing role.',
                status=ApplicationStatusEnum.PENDING,
                applied_date=datetime.now() - timedelta(days=1)
            )

        session.commit() # Commit tất cả applications


        # --- 8. Interviews ---
        print("\n--- 8. Thêm Interviews ---")
        # Lấy lại app2 đã tạo (nếu tồn tại)
        # Vì Application không có user_id, ta phải tìm qua CV và Job
        app2_for_interview = Application.query.filter(
            Application.job_id==job_frontend.id,
            Application.cv_id==cv_js1_fe.id
        ).first()

        if app2_for_interview: # Đảm bảo app2 tồn tại trước khi tạo interview cho nó
            get_or_create(session, Interview,
                application_id=app2_for_interview.id,
                dateTime=datetime.now() + timedelta(days=2),
                url='https://zoom.us/j/1234567890_interview_fe_dev'
            )
        session.commit() # Commit interviews

        # --- 9. Conversations and Messages ---
        print("\n--- 9. Thêm Conversations và Messages ---")
        # Conversation 1: Recruiter1 and Jobseeker1
        conv1 = get_or_create(session, Conversation, created_date=datetime.now() - timedelta(minutes=60))
        # Thêm người dùng vào cuộc trò chuyện (đảm bảo không thêm trùng)
        if recruiter_user1 not in conv1.users:
            conv1.users.append(recruiter_user1)
        if jobseeker_user1 not in conv1.users:
            conv1.users.append(jobseeker_user1)
        session.commit() # Commit sau khi thêm người dùng vào conversation

        get_or_create(session, Message,
            conversation_id=conv1.id,
            sender_id=recruiter_user1.id,
            content='Hi Tran, we reviewed your application for Python Developer. When are you available for an interview?',
            timestamp=datetime.now() - timedelta(minutes=50),
            is_read=False
        )
        get_or_create(session, Message,
            conversation_id=conv1.id,
            sender_id=jobseeker_user1.id,
            content='Hi! I am available on Tuesday afternoon. Does that work?',
            timestamp=datetime.now() - timedelta(minutes=40),
            is_read=True
        )

        # Conversation 2: Recruiter2 and Jobseeker2
        conv2 = get_or_create(session, Conversation, created_date=datetime.now() - timedelta(minutes=45))
        if recruiter_user2 not in conv2.users:
            conv2.users.append(recruiter_user2)
        if jobseeker_user2 not in conv2.users:
            conv2.users.append(jobseeker_user2)
        session.commit()

        get_or_create(session, Message,
            conversation_id=conv2.id,
            sender_id=recruiter_user2.id,
            content='Hi Le, your application for UX/UI Designer looks promising. Can we schedule a brief call?',
            timestamp=datetime.now() - timedelta(minutes=35),
            is_read=False
        )
        session.commit() # Commit messages

        # --- 10. Notifications ---
        print("\n--- 10. Thêm Notifications ---")
        get_or_create(session, Notification,
            user_id=jobseeker_user1.id,
            content='Your application for Frontend Developer has been confirmed.',
            is_read=False,
            created_date=datetime.now() - timedelta(minutes=30)
        )
        get_or_create(session, Notification,
            user_id=recruiter_user1.id,
            content='New application for Python Developer.',
            is_read=False,
            created_date=datetime.now() - timedelta(minutes=25)
        )
        get_or_create(session, Notification,
            user_id=jobseeker_user2.id,
            content='Your application for Data Analyst has been accepted!.',
            is_read=False,
            created_date=datetime.now() - timedelta(minutes=20)
        )
        session.commit() # Commit notifications

        print("\n--- Hoàn thành chèn dữ liệu mẫu! ---")

if __name__ == '__main__':
    with app.app_context():
        # --- QUAN TRỌNG: CÁC BƯỚC KHỞI TẠO DATABASE ---
        # 1. Đảm bảo file models.py của bạn KHÔNG có 'user_id' và 'user' relationship trong Application model
        #    nếu bạn muốn mối quan hệ gián tiếp qua CV -> Resume -> User.
        #    (Dựa trên models.py bạn đã cung cấp, nó không có user_id trong Application, nên không cần thay đổi gì).

        # 2. CHỌN MỘT TRONG HAI CÁCH DƯỚI ĐÂY TÙY VÀO TÌNH TRẠNG DỮ LIỆU CỦA BẠN:

        #    CÁCH A: (PHÙ HỢP NHẤT KHI PHÁT TRIỂN - XÓA SẠCH VÀ TẠO LẠI DB)
        #    Nếu bạn muốn xóa toàn bộ dữ liệu hiện có và tạo lại database từ đầu với schema mới,
        #    bỏ comment hai dòng dưới đây:
        print("Xóa toàn bộ database và tạo lại schema mới...")
        db.drop_all()
        db.create_all()
        print("Đã xóa và tạo lại database thành công.")

        #    CÁCH B: (KHI SỬ DỤNG FLASK-MIGRATE HOẶC DB ĐÃ CÓ DỮ LIỆU CŨ)
        #    Nếu bạn đang sử dụng Flask-Migrate để quản lý schema thay đổi,
        #    ĐỪNG BỎ COMMENT db.drop_all() và db.create_all() ở trên.
        #    Thay vào đó, bạn cần chạy các lệnh migration TRƯỚC KHI chạy script này:
        #    Trong terminal:
        #    flask db migrate -m "Removed user_id from Application model (if it was ever added)"
        #    flask db upgrade
        #    Sau đó chỉ chạy populate_sample_data() (không cần drop_all/create_all)


        # 3. Chạy hàm populate_sample_data() để thêm dữ liệu mẫu vào database
        populate_sample_data()

        print("\nKiểm tra trạng thái database sau khi chèn dữ liệu:")
        print(f"Tổng số Users: {User.query.count()}")
        print(f"Tổng số Companies: {Company.query.count()}")
        print(f"Tổng số Jobs: {Job.query.count()}")
        print(f"Tổng số Applications: {Application.query.count()}")
        print(f"Tổng số Conversations: {Conversation.query.count()}")
        print(f"Tổng số Messages: {Message.query.count()}")
        print(f"Tổng số Notifications: {Notification.query.count()}")