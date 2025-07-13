from flask import render_template

from app import app

@app.route('/')
def index():
    return render_template('index.html')



@app.route("/jobs")
def jobs():
    return render_template('jobs.html')

if __name__ == '__main__':
    from admin import *
    app.run(debug=True)