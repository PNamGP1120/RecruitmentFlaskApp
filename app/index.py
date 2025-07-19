# from sqlalchemy.sql.functions import current_user
import dbm.sqlite3

from flask import redirect, url_for, flash, session
from flask import render_template, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required

from app import app
from app import dao
from app import login
from app.models import EmploymentEnum, JobStatusEnum, ApplicationStatusEnum, RoleEnum
from app.models import Resume


@app.route('/')
def index():

    total_jobs = dao.count_jobs()
    total_candidates = dao.count_candidates()
    total_companies = dao.count_companies()

    return render_template('index.html',
                           total_jobs=total_jobs,
                           total_candidates=total_candidates,
                           total_companies=total_companies
                           )


@app.route('/profile', methods=['POST', 'GET'])
def profile_process():
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
                else:
                    # Create new resume
                    resume = Resume(**resume_data)
                    dao.add_resume(resume)
                    flash('Resume was successfully added', 'success')

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
                    else:
                        flash('Error uploading CV', 'danger')

        return redirect(url_for('profile_process'))

    return render_template('profile/profile.html', title=title, subtitle=subtitle, resume=resume, rows=cv_list)

@app.route('/company')
def company():
    title = "Company Profile"
    subtitle = "Edit your company profile"
    return render_template('profile/company.html',
                           title=title,
                           subtitle=subtitle)
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
        print(username, password)
        u = dao.auth_user(username=username, password=password)
        print(u)
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
    return  render_template('contact_us.html',
                            title=title,
                            subtitle=subtitle)

@app.route("/jobs", methods=["GET"])
def job():
    title = "JOB"
    subtitle="Welcome to Job"
    cates = dao.load_cate()
    page = int(request.args.get('page', 1))
    page_size = 3

    keyword = request.args.get("keyword")
    locate = request.args.get("location")
    jobType = request.args.get("jobType")
    category= request.args.get('category')

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
    jobs = dao.load_jobs(page=page, per_page=page_size, keyword=keyword, location=locate, employment_type=job_type_enum, category_id=category)
    locations = [loc[0] for loc in db.session.query(Job.location).distinct().all()]
    return render_template("jobs.html", title=title, subtitle=subtitle,cates=cates,jobs=jobs,locations=locations,EmploymentEnum=EmploymentEnum, selected_job_type=jobType)


@app.route("/job-detail/<int:job_id>", methods=["get"])
def job_detail(job_id):
    job = Job.query.get(job_id)
    page = int(request.args.get('page', 1))
    page_size = 3
    jobs = dao.load_jobs(page=page, per_page=page_size, location=job.location, exclude_job=job.id)
    cvs = []
    if current_user.is_authenticated:
        cvs = dao.load_cv_by_id(current_user)
    return render_template("job_detail.html", jobDetail=job, jobs=jobs, cvs=cvs, RoleEnum=RoleEnum)


@app.route("/api/apply/<int:job_id>", methods=["POST"])
@login_required
def apply_job(job_id):
    if current_user.role == RoleEnum.JOBSEEKER:
        coverLetter = request.form.get("coverLetter")
        cv = request.form.get("cv")
        if not coverLetter or not cv:
            return jsonify({"message":"Please fill in all information"}), 400
        cv_obj = CV.query.get(cv)
        if not cv_obj or cv_obj.resume.user_id!= current_user.id:
            return jsonify({"message": "Invalid CV"}), 400

        job = Job.query.get(job_id)
        if not job or job.status != JobStatusEnum.POSTED:
            return jsonify({"message":"The job does not exist or has expired"}), 400

        applycation = Application.query.filter_by(cv_id=cv, job_id=job.id).first()
        if applycation:
            return jsonify({"message": "You have already applied for this job"}), 400

        applycation = Application(cover_letter=coverLetter, status=ApplicationStatusEnum.PENDING, cv_id=cv, job_id=job.id)
        db.session.add(applycation)
        db.session.commit()
        print(applycation)
        return jsonify({"message":"You have successfully applied"}), 200
    else:
        return jsonify({"message":"You are not a job seeker!"}), 403


@app.route("/applications")
@login_required
def application():
    page = int(request.args.get("page",1))
    per_page = 3

    applies = dao.load_applications(current_user, page=page, per_page=per_page)

    total_pages = applies.pages
    for page in range(1, total_pages + 1):
        page_data = dao.load_applications(current_user, page=page, per_page=per_page)
        for a in page_data.items:
            print(f"Trang {page}: {a.cover_letter}")

    return render_template("applications.html",title="Applications", subtitle="Welcome to your applications" , applies=applies)


if __name__ == '__main__':
    with app.app_context():
        from app.admin import *

        app.run(debug=True)
