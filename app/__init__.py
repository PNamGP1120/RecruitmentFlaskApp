import os
from urllib.parse import quote
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask_dance.contrib.google import make_google_blueprint
import cloudinary
import pymysql

# Dùng PyMySQL thay cho mysqlclient
pymysql.install_as_MySQLdb()

# Cho phép OAuth không HTTPS (chỉ dev)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# Khởi tạo Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["PAGE_SIZE"] = 8

# Cấu hình database
db_user = os.environ.get("MYSQL_USER", "user")
db_password = os.environ.get("MYSQL_PASSWORD", "pass")
db_host = os.environ.get("MYSQL_HOST", "db")
db_name = os.environ.get("MYSQL_DATABASE", "recruitmentdb")

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{db_user}:{quote(db_password)}@{db_host}/{db_name}?charset=utf8mb4&ssl_disabled=true"
)

# Cấu hình Google OAuth
app.config["GOOGLE_OAUTH_CLIENT_ID"] = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")

if app.config["GOOGLE_OAUTH_CLIENT_ID"] and app.config["GOOGLE_OAUTH_CLIENT_SECRET"]:
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

# Khởi tạo extensions
db = SQLAlchemy(app)
login = LoginManager(app)

# Cấu hình Cloudinary
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True
)

# Cấu hình Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")
mail = Mail(app)

# Export các biến chính
__all__ = ["app", "db", "login", "mail"]

from app import index
