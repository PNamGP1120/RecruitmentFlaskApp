from flask import render_template, request
from app import app, db
# from utils import get_job_postings
from models import Category

@app.route('/')
def index():
    #
    # search_query = request.args.get('q', type=str)
    # location_filter = request.args.get('location', type=str)
    # category_filter_id = request.args.get('category_id', type=int)
    # employment_type_filter = request.args.get('employment_type', type=str)
    # page = request.args.get('page', 1, type=int)
    # per_page = app.config['PAGE_SIZE']
    #
    # job_postings_pagination = get_job_postings(
    #     q=search_query,
    #     location=location_filter,
    #     category_id=category_filter_id,
    #     employment_type=employment_type_filter,
    #     page=page,
    #     per_page=per_page
    # )
    #
    # categories = Category.query.all()
    #
    # return render_template(
    #     'index.html',
    #     job_postings=job_postings_pagination.items,
    #     pagination=job_postings_pagination,
    #     categories=categories,
    #     current_q=search_query,
    #     current_location=location_filter,
    #     current_category_id=category_filter_id,
    #     current_employment_type=employment_type_filter
    # )
    return 'a'

#
# @app.route('/job_postings/<job_posting_id>')
# def detail(job_posting_id):
#     return render_template('jobs.html')
# @app.route("/jobs")
# def jobs():
#     # Tái sử dụng logic từ hàm index()
#     return index()


if __name__ == '__main__':
    with app.app_context():
        from app.admin import *
        app.run(debug=True)