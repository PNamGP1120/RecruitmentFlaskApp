from flask import render_template, request
from app import app, db
from app import dao

@app.route('/')
def index():
    return render_template('index.html')


@app.route("/jobs", methods=["get"])
def job():
    cates = dao.load_cate()
    page = int(request.args.get('page', 1))
    page_size = 2
    jobs = dao.load_jobs(page=page, per_page=page_size)

    # job_title = requet

    return render_template("jobs.html", cates=cates, jobs=jobs)


if __name__ == '__main__':
    with app.app_context():
        from app.admin import *
        app.run(debug=True)