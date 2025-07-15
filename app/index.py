import flask
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user

from app import app, dao, login
from app.models import Resume


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/profile', methods=['POST', 'GET'])
def resume_process():
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
            return redirect(url_for('resume_process'))

    return render_template('profile/profile.html', title=title, subtitle=subtitle, resume=resume)

@app.route('/profile', methods=['POST', 'GET'])
def cv_process():
    return render_template()

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
    return render_template('about_us.html')


if __name__ == '__main__':
    with app.app_context():
        from app.admin import *

        app.run(debug=True)
