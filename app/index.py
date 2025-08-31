from flask import redirect, url_for, flash, abort
from flask import render_template, request, jsonify
from flask_dance.contrib.google import google
from flask_login import login_user, logout_user, current_user, login_required
from flask_socketio import join_room, leave_room, send
from app import socketio
from app.models import Conversation, Message, EmploymentEnum, RoleEnum, JobStatusEnum, ApplicationStatusEnum, Resume, CV, Job, Application, Interview
from pyexpat.errors import messages

from app import app, dao, login, mail, db
from datetime import datetime
from flask_mail import Message as MailMessage


def send_email(email, title, content):
    msg = MailMessage(
        subject=title,
        recipients=[email],
        body=content
    )
    mail.send(msg)
    return 'Email sent successfully!'

@app.context_processor
def inject_user():
    is_recruiter = current_user.is_authenticated and current_user.role == RoleEnum.RECRUITER
    is_jobSeeker = current_user.is_authenticated and current_user.role == RoleEnum.JOBSEEKER
    is_admin = current_user.is_authenticated and current_user.role == RoleEnum.ADMIN
    is_verified_recruiter = current_user.is_authenticated and current_user.is_recruiter == True

    return dict(is_recruiter=is_recruiter, is_jobSeeker=is_jobSeeker, is_admin=is_admin, is_verified_recruiter=is_verified_recruiter)


@app.context_processor
def inject_enums():
    return dict(ApplicationStatusEnum=ApplicationStatusEnum)


@app.context_processor
def inject_notifications():
    if current_user.is_authenticated:
        page = int(request.args.get('page', 1))
        per_page = 5

        pagination = dao.NotificationDAO.get_all(current_user.id, page=page, per_page=per_page)
        notis = pagination.items
        unread_notifications = dao.NotificationDAO.get_unread(current_user.id)

        return dict(notifications=notis,
                    unread_notifications=unread_notifications,
                    notification_pagination=pagination)
    return {}


@app.route('/')
def index():
    total_jobs = dao.count_jobs()
    total_candidates = dao.count_candidates()
    total_companies = dao.count_companies()

    return render_template('index.html',
                           total_jobs=total_jobs,
                           total_candidates=total_candidates,
                           total_companies=total_companies,
                           )


@app.route('/profile', methods=['POST', 'GET'])
@login_required
def profile_process():
    if current_user.is_authenticated:
        if current_user.role == RoleEnum.RECRUITER:
            data_company = dao.load_company_by_id(current_user.id)

            if request.method == 'POST':
                form_data = {
                    'website': request.form.get('website', ''),
                    'introduction': request.form.get('introduction', ''),
                    'company_name': request.form.get('company_name', ''),
                    'industry': request.form.get('industry', ''),
                    'company_size': request.form.get('company_size', ''),
                    'address': request.form.get('address', ''),
                }
                if data_company:
                    dao.update_company(data_company, form_data)
                    flash('Company was successfully updated', 'success')
                    dao.NotificationDAO.create(user_id=current_user.id,
                                               content="Your company profile has been updated.")
                else:
                    form_data['user_id'] = current_user.id
                    dao.add_company(form_data)
                    flash('Company was successfully added', 'success')
                    dao.NotificationDAO.create(user_id=current_user.id,
                                               content="You have successfully created your company profile.")

            data_company = dao.load_company_by_id(current_user.id)

            if not data_company:
                data_company = {
                    'website': '',
                    'introduction': '',
                    'company_name': '',
                    'industry': '',
                    'company_size': '',
                    'address': '',
                }

            title = "Company Profile"
            subtitle = "Edit your company profile"
            print(current_user.company)
            return render_template('profile/company.html',
                                   data_company=data_company,
                                   title=title,
                                   subtitle=subtitle)

        elif current_user.role == RoleEnum.JOBSEEKER:

            title = "Resume & CV Management"
            subtitle = "Edit your resume & CV"

            # Fetch the current user's resume (if it exists)
            resume = Resume.query.filter_by(user_id=current_user.id).first()
            cv_list = CV.query.filter_by(resume_id=resume.id).all() if resume else []

            if request.method == 'POST':
                if 'resume_form' in request.form:
                    if (not request.form['skill'] or not request.form['experience'] or not request.form['education']
                            or not request.form['location'] or not request.form['job'] or not request.form['linkedin']):
                        flash('Please enter all required resume details', 'danger')
                    else:
                        # Prepare resume data
                        resume_data = {
                            'skill': request.form['skill'],
                            'experience': request.form['experience'],
                            'education': request.form['education'],
                            'preferred_locations': request.form['location'],
                            'preferred_job_types': request.form['job'],
                            'linkedin_url': request.form.get('linkedin', '')
                        }
                        # Update or create resume
                        if resume:
                            # Update existing resume
                            dao.update_resume(resume, resume_data)
                            flash('Resume was successfully updated', 'success')
                            dao.NotificationDAO.create(user_id=current_user.id, content="Your resume has been updated.")
                        else:
                            # Create new resume
                            resume = Resume(**resume_data)
                            dao.add_resume(resume)
                            flash('Resume was successfully added', 'success')
                            dao.NotificationDAO.create(user_id=current_user.id,
                                                       content="You have successfully created your resume.")

                elif 'cv_form' in request.form:  # Handle CV form submission
                    title = request.form['title']
                    file = request.files['file']
                    is_default = 'default' in request.form

                    if not resume:
                        flash('Please create a resume before uploading a CV', 'danger')
                    elif not title or not file:
                        flash('Please provide a title and file for the CV', 'danger')
                    else:
                        # Validate file type
                        if not file.filename.lower().endswith('.pdf'):
                            flash('Only PDF files are allowed', 'danger')
                        else:
                            success = dao.add_cv(
                                title=title,
                                file=file,
                                is_default=is_default,
                                resume_id=resume.id if resume else None
                            )
                            if success:
                                flash('CV was successfully uploaded', 'success')
                                dao.NotificationDAO.create(user_id=current_user.id,
                                                           content=f'Your CV "{title}" has been uploaded.')
                            else:
                                flash('Error uploading CV', 'danger')

                elif 'update_cv_form' in request.form:  # Handle CV update form submission
                    cv_id = request.form['cv_id']
                    title = request.form['title']
                    file = request.files['file']  # This will be an empty FileStorage object if no file is selected
                    is_default = 'default' in request.form

                    if not cv_id or not title:
                        flash('CV ID and title are required for update', 'danger')
                    else:
                        cv_to_update = CV.query.get(cv_id)
                        if not cv_to_update or cv_to_update.resume.user_id != current_user.id:
                            flash('Invalid CV or unauthorized access', 'danger')
                        else:
                            # Validate file type if a new file is provided
                            if file and file.filename and not file.filename.lower().endswith('.pdf'):
                                flash('Only PDF files are allowed for CV updates', 'danger')
                            else:
                                success = dao.update_cv(
                                    cv=cv_to_update,
                                    title=title,
                                    file=file if file and file.filename else None,
                                    # Pass file only if a new one is selected
                                    is_default=is_default,
                                    resume_id=resume.id if resume else None
                                )
                                if success:
                                    flash('CV was successfully updated', 'success')
                                    dao.NotificationDAO.create(user_id=current_user.id,
                                                               content=f'Your CV "{title}" has been updated.')

                                else:
                                    flash('Error updating CV', 'danger')

                return redirect(url_for('profile_process'))

    return render_template('profile/profile.html', title=title, subtitle=subtitle, resume=resume, rows=cv_list)


@app.route('/delete_cv', methods=['POST'])
def delete_cv():
    cv_id = request.form.get('cv_id')
    if not cv_id:
        flash('CV ID is required', 'danger')
        return redirect(url_for('profile_process'))

    cv = CV.query.get(cv_id)
    if not cv or cv.resume.user_id != current_user.id:
        flash('Invalid CV or unauthorized access', 'danger')
        return redirect(url_for('profile_process'))

    # Check if CV is used in any applications
    if cv.applications:
        flash('Cannot delete CV because it is used in one or more applications', 'danger')
        return redirect(url_for('profile_process'))

    success = dao.delete_cv(cv)
    if success:
        flash('CV was successfully deleted', 'success')
        dao.NotificationDAO.create(
            user_id=current_user.id,
            content=f'Your CV "{cv.title}" was successfully deleted.'
        )
    else:
        flash('Error deleting CV', 'danger')
    return redirect(url_for('profile_process'))


@app.route("/register", methods=['GET', 'POST'])
def register_process():
    err_msg = None
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            err_msg = "Passwords do not match."
        else:
            data = request.form.copy()
            data.pop('confirm_password', None)
            avatar = request.files.get('avatar')
            dao.add_user(avatar, **data)
            return redirect(url_for('login_process'))

    title = "Create Your Account"
    subtitle = "Join our platform and discover thousands of job opportunities."
    return render_template('register.html', err_msg=err_msg, title=title, subtitle=subtitle)


@app.route("/login", methods=['GET', 'POST'])
def login_process():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        # print(username, password)
        u = dao.auth_user(username=username, password=password)
        # print(u)
        if u:
            login_user(u)
            next = request.args.get('next')
            return redirect(next if next else url_for('index'))
    title = "Account Login"
    subtitle = "Please enter your credentials to proceed."
    return render_template('login.html', title=title, subtitle=subtitle)


@app.route("/login/google")
def google_initiate_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    # Nếu đã được ủy quyền (authorized) rồi, chuyển hướng về trang chính.
    return redirect(url_for("index"))


@app.route("/login/google/callback")
def google_authorized():
    if not google.authorized:
        flash("Đăng nhập bằng Google thất bại: Người dùng chưa cấp quyền.", "danger")
        return redirect(url_for("login_process"))

    resp = google.get("/oauth2/v2/userinfo")
    if resp.ok:
        info = resp.json()
        email = info.get("email")
        name = info.get("name")
        avatar_url = info.get("picture")

        if not email:
            flash("Đăng nhập bằng Google thất bại: Không lấy được email.", "danger")
            return redirect(url_for("login_process"))

        # Tìm người dùng theo email
        user = dao.get_user_by_email(email)  # Giả sử bạn đã có hàm này trong dao.py

        if not user:
            # GỌI HÀM DAO VÀ GÁN KẾT QUẢ VÀO BIẾN 'user'
            user = dao.add_user_google(
                username=email.split('@')[0],
                email=email,
                first_name=name.split(' ')[0] if name else '',
                last_name=' '.join(name.split(' ')[1:]) if name else '',
                avatar=avatar_url,
                role='JOBSEEKER',  # Truyền chuỗi, không phải enum
                password='google_user_password_placeholder'
            )
            flash("Tạo tài khoản thành công!", "success")

        # Sau khi đảm bảo biến 'user' đã có giá trị
        if user:
            login_user(user)
            flash("Đăng nhập bằng Google thành công!", "success")
            return redirect(url_for("index"))
        else:
            # Xử lý trường hợp add_user_google thất bại
            flash("Đăng nhập bằng Google thất bại", "danger")
            return redirect(url_for("login_process"))

    # Trường hợp resp.ok == False
    flash("Đăng nhập bằng Google thất bại", "danger")
    return redirect(url_for("login_process"))


@app.route("/logout")
def logout_process():
    logout_user()
    return redirect(url_for('login_process'))


@login.user_loader
def get_user_by_id(user_id):
    return dao.get_user_by_id(user_id)


@app.route('/about')
def about():
    title = "About Us"
    subtitle = "Learn more about our company and our services."
    return render_template('about_us.html',
                           title=title,
                           subtitle=subtitle)


@app.route('/contact')
def contact():
    title = "Contact Us"
    subtitle = "Get in touch with us for any questions or inquiries."
    return render_template('contact_us.html',
                           title=title,
                           subtitle=subtitle)


@app.route("/jobs", methods=["GET"])
def job():
    title = "JOB"
    subtitle = "Welcome to Job"
    cates = dao.load_cate()
    page = int(request.args.get('page', 1))
    page_size = 3

    keyword = request.args.get("keyword")
    locate = request.args.get("location")
    jobType = request.args.get("jobType")
    category = request.args.get('category')

    if not locate or locate == "Choose city":
        locate = None

    if not category or category == "Choose Category":
        category = None

    job_type_enum = None

    if jobType:
        try:
            job_type_enum = EmploymentEnum[jobType]  # vi du "FULLTIME" -> EmploymentEnum.FULLTIME
        except KeyError:
            print(f"[!] jobType không hợp lệ: {jobType}")
    jobs = dao.load_jobs(page=page, per_page=page_size, keyword=keyword, location=locate, employment_type=job_type_enum,
                         category_id=category)
    locations = [loc[0] for loc in db.session.query(Job.location).distinct().all()]
    return render_template("jobs.html", title=title, subtitle=subtitle, cates=cates, jobs=jobs, locations=locations,
                           EmploymentEnum=EmploymentEnum, selected_job_type=jobType)


@app.route("/job-detail/<int:job_id>", methods=["get"])
def job_detail(job_id):
    job = Job.query.get(job_id)
    page = int(request.args.get('page', 1))
    page_size = 3
    jobs = dao.load_jobs(page=page, per_page=page_size, location=job.location, exclude_job=job.id)
    cvs = []
    if current_user.is_authenticated and current_user.role == RoleEnum.JOBSEEKER:
        cvs = dao.load_cv_by_id(current_user.id)

    applications = []
    if current_user.is_authenticated and current_user.role == RoleEnum.RECRUITER and job.company_id == current_user.company.id:
        applications = dao.load_applications_for_company(current_user.id, page=page, per_page=page_size)
        print(applications)
        content = f"Nhà tuyển dụng đã xem hồ sơ của bạn cho công việc '{job.title}'."
        # dao.NotificationDAO.create(user_id=applications.jobseeker_id, content=content)
        # for app in applications.items:
        #     dao.NotificationDAO.create(user_id=app.jobseeker_id, content=content)

    return render_template("job_detail.html", jobDetail=job, jobs=jobs, cvs=cvs, RoleEnum=RoleEnum,
                           applies=applications, now = datetime.utcnow())


@app.route("/api/apply/<int:job_id>", methods=["POST"])
@login_required
def apply_job(job_id):
    if current_user.role == RoleEnum.JOBSEEKER:
        coverLetter = request.form.get("coverLetter")
        cv = request.form.get("cv")
        if not coverLetter or not cv:
            return jsonify({"message": "Please fill in all information"}), 400
        cv_obj = CV.query.get(cv)
        if not cv_obj or cv_obj.resume.user_id != current_user.id:
            return jsonify({"message": "Invalid CV"}), 400

        job = Job.query.get(job_id)
        if not job or job.status != JobStatusEnum.POSTED:
            return jsonify({"message": "The job does not exist or has expired"}), 400

        applycation = Application.query.filter_by(cv_id=cv, job_id=job.id).first()
        if applycation:
            return jsonify({"message": "You have already applied for this job"}), 400

        applycation = Application(cover_letter=coverLetter, status=ApplicationStatusEnum.PENDING, cv_id=cv,
                                  job_id=job.id)
        db.session.add(applycation)
        db.session.commit()
        print(applycation)

        recruiter_id = job.company.user_id
        content = f"{current_user.username} has just applied for your job: {job.title}"
        dao.NotificationDAO.create(user_id=current_user.id, content=content)
        dao.NotificationDAO.create(user_id=recruiter_id, content=content)

        return jsonify({"message": "You have successfully applied"}), 200
    else:
        return jsonify({"message": "You are not a job seeker!"}), 403


@app.route("/applications")
@login_required
def application():
    page = max(1, int(request.args.get("page", 1)))
    per_page = 3
    status = request.args.get("status")

    if current_user.role == RoleEnum.JOBSEEKER:
        if status == "All" or status == "Choose Status":
            status = None
        applies = dao.load_applications_for_user(current_user, page=page, per_page=per_page, status=status)
        list_interview = []
        for a in applies:
            interview = dao.get_interview(a.id)
            if interview:
                list_interview.append(interview)
        interview_map = {i.application_id: i for i in list_interview}
        return render_template("applications.html", title="Applications",
                               subtitle="List of your applications", applies=applies, interview_map=interview_map)
    elif current_user.role == RoleEnum.RECRUITER:
        if status == "All" or status == "Choose Status":
            status = None
        applies = dao.load_applications_for_company(current_user.id, page=page, per_page=per_page, status=status)
        list_interview = []
        for a in applies:
            interview = dao.get_interview(a.id)
            if interview:
                list_interview.append(interview)
        interview_map = {i.application_id: i for i in list_interview}
        print("interview_map", interview_map)
        return render_template("applications.html", title="Applications",
                               subtitle="List of applications for your company", applies=applies, interview_map=interview_map)
    return render_template("applications.html", title="Applications",
                           subtitle="List of applications for your company")


# Recruiter
@app.route('/job-posting', methods=['GET', 'POST'])
def job_posting():
    title = "Job Posting"
    subtitle = "Post your job here"
    page = int(request.args.get('page', 1))
    page_size = 5

    company = dao.load_company_by_id(current_user.id)
    # if not company:
    #     return jsonify({"message": "You don't have a company yet"})
    print("company id", company.id)
    jobs = dao.load_jobs(company_id=company.id, page=page, per_page=page_size, status=None)

    cates = dao.load_cate()

    print(dao.load_company_by_id(current_user.id).id)
    employment_enum = EmploymentEnum
    print(employment_enum.FULLTIME)
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        requirements = request.form.get('requirements')
        location = request.form.get('location')
        salary = request.form.get('salary')
        employment_type = request.form.get('employment_type')
        status = request.form.get('status')
        expiration_date = request.form.get('expiration_date')
        category_id = request.form.get('category_id')
        print(category_id)

        if 'save_draft' in request.form:
            status = 'DRAFT'
        else:
            status = 'POSTED'

        dao.add_job(
            company_id=dao.load_company_by_id(current_user.id).id,
            title=title,
            description=description,
            requirements=requirements,
            location=location,
            salary=salary,
            employment_type=employment_type,
            status=status,
            expiration_date=expiration_date,
            category_id=category_id,
        )
        dao.NotificationDAO.create(
            user_id=current_user.id,
            content=f"You successfully {'saved a draft' if status == 'DRAFT' else 'posted'} the job: {title}"
        )

        flash('Job was successfully added', 'success')
        return redirect(url_for('job_posting'))

    return render_template('recruiter/job_posting.html',
                           title=title,
                           subtitle=subtitle,
                           jobs=jobs,
                           categories=cates,
                           employment_types=employment_enum, )


@app.route("/api/verified-apply/<int:apply_id>", methods=['POST'])
@login_required
def verified_apply(apply_id):
    if not current_user.is_recruiter:
        return jsonify({"message": "You are not a recruiter"}), 403
    apply = dao.get_application_by_id(apply_id)
    if not apply:
        return jsonify({"error": "Application not found"}), 404
    if apply.job.company_id != current_user.company.id:
        print(apply.job.company_id, current_user.company.id, current_user.username)
        return jsonify({"message": "You are not the owner of this job posting"}), 403

    med = request.form.get("med")
    if med == "Confirm":
        apply.status = ApplicationStatusEnum.CONFIRMED
        # con xu ly tao lich phong van
        dao.NotificationDAO.create(user_id=apply.cv.resume.user_id,
                                   content=f"Your application for {apply.job.title} has been confirmed.")
    elif med == "Reject":
        apply.status = ApplicationStatusEnum.REJECTED
        dao.NotificationDAO.create(user_id=apply.cv.resume.user_id,
                                   content=f"Your application for {apply.job.title} has been rejected.")
    elif med == "Accept":
        apply.status = ApplicationStatusEnum.ACCEPTED
        dao.NotificationDAO.create(user_id=apply.cv.resume.user_id,
                                   content=f"Your application for {apply.job.title} has been accepted.")
    else:
        return jsonify({"error": "Invalid value for med"}), 400

    db.session.commit()
    return jsonify({"message": f"{med} successfully"}), 200


@app.route("/notifications")
@login_required
def notifications():
    title = 'Your notifications'
    subtitle = 'All your important updates appear here'

    return render_template('notifications.html',
                           title=title,
                           subtitle=subtitle,
                           )


@app.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    dao.NotificationDAO.mark_all_as_read(current_user.id)
    return redirect(request.referrer or url_for('index'))


@app.route('/notifications/<int:notification_id>')
@login_required
def notification_detail(notification_id):
    notification = dao.NotificationDAO.get_by_id(notification_id)

    if notification is None or notification.user_id != current_user.id:
        abort(404)

    if not notification.is_read:
        dao.NotificationDAO.mark_as_read(notification_id, current_user.id)

    return render_template('notification_detail.html', notification=notification)


@app.route('/notification/<int:notification_id>/mark-read', methods=['POST'])
def mark_notification_as_read(notification_id):
    # Example: mark notification as read in the database
    dao.NotificationDAO.mark_as_read(notification_id, current_user.id)
    return redirect(url_for('notifications'))

@app.route("/verified", methods=['get'])
@login_required
def verified_user():
    if current_user.role != RoleEnum.ADMIN:
        return jsonify({"message": "You are not an admin!"}, 403)
    else:
        page = int(request.args.get("page", 1))
        per_page = 2
        listRecruiter = dao.get_list_recruiter(page=page, per_page=per_page)
        print("listUser", listRecruiter)
        return render_template("verified_user.html", title="Verified recruiter", subtitle="Welcome admin", listRecruiter=listRecruiter)


@app.route("/api/verified-recruiter/<int:user_id>", methods=["POST"])
@login_required
def verified_recruiter(user_id):
    if current_user.role != RoleEnum.ADMIN:
        return jsonify({"status": 403})
    user = dao.get_user_by_id(user_id)
    if user.role == RoleEnum.RECRUITER:
        user.is_recruiter = True
        db.session.commit()
        print("success")
        return jsonify({"status": 200})
    else:
        return jsonify({"status": 400})



@app.route("/api/cancel-recruiter/<int:user_id>", methods=["POST"])
@login_required
def cancel_recruiter(user_id):
    print("hello")
    if current_user.role != RoleEnum.ADMIN:
        jsonify({"status": 403})
    user = dao.get_user_by_id(user_id)
    if user.role == RoleEnum.RECRUITER:
        user.is_recruiter = False
        db.session.commit()
        return jsonify({"status": 200})
    else:
        return jsonify({"status": 400})


@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        print("Webhook received:", data)

        if data.get("ref") == "refs/heads/develop":
            print("Đúng nhánh develop - bắt đầu xử lý...")
            # Gọi script hoặc hành động CICD ở đây
        else:
            print("Webhook không đến từ nhánh develop")

        return "", 204

    except Exception as e:
        print("Error in webhook:", str(e))
        return jsonify({"error": str(e)}), 400


# Chat
@app.route('/conversations')
@login_required
def conversations_list():
    convs = dao.get_conversations_for_user(current_user.id)
    return render_template('conversations.html',
                           title="Your Conversations",
                           subtitle="All your chats are here",
                           conversations=convs)


@app.route('/chat/<int:conversation_id>')
@login_required
def chat_room(conversation_id):
    """Vào phòng chat cụ thể."""
    conv = dao.get_conversation_by_id(conversation_id)
    if not conv or current_user not in conv.users:
        abort(403) # Không có quyền truy cập

    # Lấy người nhận (người còn lại trong cuộc trò chuyện)
    recipient = next((user for user in conv.users if user.id != current_user.id), None)

    return render_template('chat.html',
                           conversation=conv,
                           recipient=recipient,
                           messages=conv.messages)


@app.route('/start_chat/<int:recruiter_id>')
@login_required
def start_chat(recruiter_id):
    if current_user.role != RoleEnum.JOBSEEKER:
        flash("Only job seekers can start a conversation.", "warning")
        return redirect(request.referrer or url_for('index'))

    recruiter = dao.get_user_by_id(recruiter_id)
    if not recruiter or recruiter.role != RoleEnum.RECRUITER:
        flash("Recruiter not found.", "danger")
        return redirect(url_for('index'))

    conv = dao.get_or_create_conversation(current_user.id, recruiter_id)
    if conv:
        return redirect(url_for('chat_room', conversation_id=conv.id))
    else:
        flash("Could not start conversation.", "danger")
        return redirect(url_for('index'))

@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    print(f"{current_user.username} has entered the room: {room}")


@socketio.on('message')
def handle_message(data):
    room = data['room']
    content = data['data']
    conversation_id = int(room)

    # Lưu tin nhắn vào DB
    msg = dao.add_message(
        conversation_id=conversation_id,
        sender_id=current_user.id,
        content=content
    )

    # Gửi tin nhắn đến tất cả client trong phòng
    response = {
        "sender": current_user.username,
        "avatar": current_user.avatar,
        "message": msg.content,
        "timestamp": msg.timestamp.strftime("%b %d, %I:%M %p")
    }
    send(response, to=room)
    print(f"Message from {current_user.username} to room {room}: {content}")

@app.route('/recruiter/start_chat/<int:jobseeker_id>')
@login_required
def recruiter_start_chat(jobseeker_id):
    if current_user.role != RoleEnum.RECRUITER:
        flash("Only recruiters can start this conversation.", "warning")
        return redirect(request.referrer or url_for('index'))

    jobseeker = dao.get_user_by_id(jobseeker_id)
    if not jobseeker or jobseeker.role != RoleEnum.JOBSEEKER:
        flash("Job seeker not found.", "danger")
        return redirect(url_for('index'))

    conv = dao.get_or_create_conversation(current_user.id, jobseeker_id)
    if conv:
        # Tạo thông báo cho người tìm việc
        notification_content = f"Recruiter '{current_user.username}' from '{current_user.company.company_name}' has started a conversation with you."
        dao.NotificationDAO.create(user_id=jobseeker_id, content=notification_content)

        return redirect(url_for('chat_room', conversation_id=conv.id))
    else:
        flash("Could not start conversation.", "danger")
        return redirect(url_for('index'))

"""
    Chức năng thống kê cho nhà tuyển dụng:
    Thống kê số lượng don ung tuyen cua cong ty theo thang quy nam
    
"""
@app.route("/stats-by-recruiter")
@login_required
def stats_by_recruiter():
    if current_user.role != RoleEnum.RECRUITER:
        return jsonify({"status": 403})
    check_company = dao.is_company_exist(current_user.id)
    if not check_company:
        return jsonify({"message": "Bạn chưa có công ty hoặc không phải chủ công ty này", "status": 404})
    company=dao.load_company_by_id(current_user.id)
    stats = dao.stats_job_by_recruiter(company_id=company.id)
    stats = [dict(row._mapping) for row in stats]
    print("stats", stats)

    list_job = dao.get_job_by_company_id(company_id=company.id, year=datetime.now().year)
    if not list_job:
        return jsonify({"message": "Bạn chưa có job nào", "status": 400})

    stats_application = []
    for job in list_job:
        stats_application.append(dao.stats_application_by_recruiter(job_id=job))

    print("application-stats",stats_application)
    title = 'statistics and reports'
    subtitle = ''
    return render_template("recruiter/stats_for_recruiter.html", title=title,
                           subtitle=subtitle, stats=stats, stast_applies = stats_application, year=datetime.now().year)


@app.route("/api/<int:application_id>/create_link", methods=["post"])
@login_required
def create_interview_link(application_id):
    if current_user.role != RoleEnum.RECRUITER:
        return jsonify({"status": 403})
    check_company = dao.is_company_exist(current_user.id)
    if not check_company:
        return jsonify({"message": "Bạn chưa có công ty hoặc không phải chủ công ty này", "status": 404})
    interview = db.session.query(Interview).filter(Interview.application_id==application_id).first()
    if interview:
        return jsonify({"link": interview.url, "status": 200})

    interview_date = request.form.get("date")
    application=dao.get_application_by_id(application_id)
    job = application.job
    user = dao.get_user_by_application_id(application_id)
    print("email", user.id, user.email)
    link = dao.create_interview_link(application_id, interview_date)
    title="Xác nhận trúng tuyển"
    content=(f"Chúc mừng {user.username} đã trúng tuyển cho công việc {job.title} \n Bạn vui lòng tham gia phỏng vấn vào thời gian và địa điểm theo thông báo bên dưới \n"
             f"Thời gian: {interview_date} \n"
             f"Link phỏng vấn online (vòng 1): {link}")
    send_email(user.email, title, content)
    return jsonify({"link": link, "status": 201})



@app.route("/<int:user_id>/interview")
def list_interview(user_id):
    list_interview = dao.get_list_interview_by_owner_company(user_id)
    title="List interview for your company"
    return render_template("list_interview.html", title=title , list_interview=list_interview )


@app.route("/company/<int:company_id>")
def view_company(company_id):
    company = dao.get_company_by_id(company_id=company_id)
    return render_template("view_company.html", title="View Company", company=company)


@app.route("/settings")
def setting():
    return render_template("setting.html", title="Setting")

if __name__ == '__main__':
    with app.app_context():
        from app.admin import *

        socketio.run(app, host="0.0.0.0", port=5000, debug=True)
        # app.run(debug=True)