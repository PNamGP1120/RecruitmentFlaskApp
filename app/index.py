from flask import render_template, request
from app import app, db
# from utils import get_job_postings
from app.models import Category

@app.route('/')
def index():
    
    return render_template('index.html')

#
# @app.route('/job_postings/<job_posting_id>')
# def detail(job_posting_id):
#     return render_template('jobs.html')


@app.route("/jobs")
def jobs():
    
    return render_template('jobs.html')




if __name__ == '__main__':
    with app.app_context():
        from app import admin
        app.run(debug=True)