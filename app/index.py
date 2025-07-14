from flask import render_template, request, redirect, url_for
from flask_login import login_user, logout_user, current_user

# from sqlalchemy.sql.functions import current_user

from app import app, dao, login
from app.models import RoleEnum


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

@app.route('/profile')
def profile():
    if current_user.is_authenticated:
        if current_user.role == RoleEnum.RECRUITER:
            return redirect(url_for('company'))
        elif current_user.role == RoleEnum.JOBSEEKER:
            return redirect(url_for('jobseeker_profile'))
    else:
        return redirect(url_for('login_process'))
    title = "Resume & CV Management"
    subtitle = "Edit your resume & CV"
    return render_template('profile/profile.html', title=title, subtitle=subtitle)

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
        u = dao.auth_user(username = username, password = password)
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

if __name__ == '__main__':
    with app.app_context():
        from app.admin import *
        app.run(debug=True)