# from sqlalchemy.sql.functions import current_user

from flask import redirect, url_for, flash, abort
from flask import render_template, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required

from app import app, dao, login
from app.models import EmploymentEnum, RoleEnum
from app.models import JobStatusEnum, ApplicationStatusEnum
from app.models import Resume


@app.context_processor
def inject_user():
    is_recruiter = current_user.is_authenticated and current_user.role == RoleEnum.RECRUITER
    is_jobSeeker = current_user.is_authenticated and current_user.role == RoleEnum.JOBSEEKER
    is_admin = current_user.is_authenticated and current_user.role == RoleEnum.ADMIN

    return dict(is_recruiter=is_recruiter, is_jobSeeker=is_jobSeeker, is_admin=is_admin)


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

    # chuyen chuoi thanh enum
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
        content = f"Nhà tuyển dụng đã xem hồ sơ của bạn cho công việc '{job.title}'."
        dao.NotificationDAO.create(user_id=applications.jobseeker_id, content=content)

    return render_template("job_detail.html", jobDetail=job, jobs=jobs, cvs=cvs, RoleEnum=RoleEnum,
                           applies=applications)


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
        return render_template("applications.html", title="Applications",
                               subtitle="List of your applications", applies=applies)
    elif current_user.role == RoleEnum.RECRUITER:
        if status == "All" or status == "Choose Status":
            status = None
        applies = dao.load_applications_for_company(current_user.id, page=page, per_page=per_page, status=status)
        return render_template("applications.html", title="Applications",
                               subtitle="List of applications for your company", applies=applies)
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


if __name__ == '__main__':
    with app.app_context():
        from app.admin import *

        app.run(host="0.0.0.0", port=5000, debug=True)
