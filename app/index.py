from flask import render_template, request
from app import app, db
from app import dao
from app.models import EmploymentEnum


@app.route('/')
def index():
    return render_template('index.html')


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