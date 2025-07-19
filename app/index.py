# from sqlalchemy.sql.functions import current_user
from flask import redirect, url_for, flash
from flask import render_template, request
from flask_login import login_user, logout_user, current_user, login_required

from app import app
from app import dao
from app import login
from app.models import EmploymentEnum, RoleEnum
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
@login_required
def profile_process():


    if current_user.is_authenticated:
        if current_user.role == RoleEnum.RECRUITER :
            data_company = dao.load_company_by_id(current_user.id)

            if request.method == 'POST':
                form_data ={
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
                else:
                    form_data['user_id'] = current_user.id
                    dao.add_company(form_data)
                    flash('Company was successfully added', 'success')

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
        elif current_user.role == RoleEnum.JOBSEEKER :
            title = "Resume & CV Management"
            subtitle = "Edit your resume & CV"
            # Fetch the current user's resume (if it exists)
            resume = Resume.query.filter_by(user_id=current_user.id).first()

            if request.method == 'POST':
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
                    return redirect(url_for('profile_process'))

            return render_template('profile/profile.html', title=title, subtitle=subtitle, resume=resume)
        return None
    else:
        return redirect(url_for('index'))

@app.route('/company')
def company():
    title = "Company Profile"
    subtitle = "Edit your company profile"
    print(current_user.role)
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
    cates = dao.load_cate()
    page = int(request.args.get('page', 1))
    page_size = 3

    keyword = request.args.get("keyword")
    locate = request.args.get("location")
    jobType = request.args.get("jobType")

    if not locate or locate == "Choose city":
        locate = None

    # chuyen chuoi thanh enum
    job_type_enum = None

    if jobType:
        try:
            job_type_enum = EmploymentEnum[jobType]  # vi du "FULLTIME" -> EmploymentEnum.FULLTIME
        except KeyError:
            print(f"[!] jobType không hợp lệ: {jobType}")
    jobs = dao.load_jobs(page=page, per_page=page_size, keyword=keyword, location=locate, employment_type=job_type_enum)
    locations = [loc[0] for loc in db.session.query(Job.location).distinct().all()]
    return render_template("jobs.html",cates=cates,jobs=jobs,locations=locations,EmploymentEnum=EmploymentEnum, selected_job_type=jobType)


@app.route("/job-detail/<int:job_id>", methods=["get"])
def job_detail(job_id):
    job = Job.query.get(job_id)

    return render_template("job_detail.html", job=job)



if __name__ == '__main__':
    with app.app_context():
        from app.admin import *

        app.run(debug=True)
