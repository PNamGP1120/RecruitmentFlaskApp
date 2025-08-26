# import os
#
# import cloudinary
# from flask import Flask
# from flask_mail import Mail
# from flask_sqlalchemy import SQLAlchemy
# from urllib.parse import quote
# from flask_login import LoginManager
# from flask_dance.contrib.google import make_google_blueprint, google
#
# os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
#
# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'jikagfvcuyidwsfgdsfhahfadgdhdfhbssgvvudbsjahfduyjfvdguieygvsfuy'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:%s@localhost/recruitmentdb?charset=utf8mb4' % quote(
#     "Phuongnam0212@")
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# app.config["PAGE_SIZE"] = 8
#
# app.config["GOOGLE_OAUTH_CLIENT_ID"] = "310143509450-erjdeni7iprik2u725hkil1i3a9dg9ud.apps.googleusercontent.com"
# app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = "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"
# # app.config["GOOGLE_REDIRECT_URI"] = "http://localhost:5000/login/callback"
#
# google_bp = make_google_blueprint(
#     client_id=app.config["GOOGLE_OAUTH_CLIENT_ID"],
#     client_secret=app.config["GOOGLE_OAUTH_CLIENT_SECRET"],
#     # redirect_to="google_login",
#     redirect_to="google_authorized",
#     scope=[
#         "https://www.googleapis.com/auth/userinfo.profile",
#         "https://www.googleapis.com/auth/userinfo.email",
#         "openid"
#     ]
# )
#
# app.register_blueprint(google_bp, url_prefix="/login")
#
# db = SQLAlchemy(app)
# login = LoginManager(app)
#
# cloudinary.config(
#     cloud_name="dqpu49bbo",
#     api_key="743773348627895",
#     api_secret="EF7elKsibuI8JEBqfMNZYYWUYvo",
#     secure=True
# )
#
# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = 'phuongnam.it0212@gmail.com'
# app.config['MAIL_PASSWORD'] = 'Phuongnam0212'
#
# mail = Mail(app)


import os
from urllib.parse import quote
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask_dance.contrib.google import make_google_blueprint, google
import cloudinary

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["PAGE_SIZE"] = 8

# DATABASE
db_user = os.environ.get("MYSQL_USER", "root")
db_password = os.environ.get("MYSQL_PASSWORD", "Phuongnam0212@")
db_host = os.environ.get("MYSQL_HOST", "db")       # db là service trong Docker
db_name = os.environ.get("MYSQL_DATABASE", "recruitmentdb")
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{quote(db_password)}@{db_host}/{db_name}?charset=utf8mb4'

# GOOGLE OAUTH
app.config["GOOGLE_OAUTH_CLIENT_ID"] = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
google_bp = make_google_blueprint(
    client_id=app.config["GOOGLE_OAUTH_CLIENT_ID"],
    client_secret=app.config["GOOGLE_OAUTH_CLIENT_SECRET"],
    redirect_to="google_authorized",
    scope=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid"
    ]
)
app.register_blueprint(google_bp, url_prefix="/login")

# INIT EXTENSIONS
db = SQLAlchemy(app)
login = LoginManager(app)

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True
)

# MAIL
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")
mail = Mail(app)
