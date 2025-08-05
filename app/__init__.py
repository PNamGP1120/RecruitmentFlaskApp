import cloudinary
from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote
from flask_login import LoginManager
from flask_dance.contrib.google import make_google_blueprint, google

app = Flask(__name__)
app.config['SECRET_KEY']='jikagfvcuyidwsgvvudbsjahfduyjfvdguieygvsfuy'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:%s@localhost/recruitmentdb?charset=utf8mb4' % quote("Phuongnam0212@")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config["PAGE_SIZE"] = 8

app.config["GOOGLE_OAUTH_CLIENT_ID"] = "310143509450-erjdeni7iprik2u725hkil1i3a9dg9ud.apps.googleusercontent.com"
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = "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"

google_bp = make_google_blueprint(
    client_id=app.config["GOOGLE_OAUTH_CLIENT_ID"],
    client_secret=app.config["GOOGLE_OAUTH_CLIENT_SECRET"],
    redirect_to="google_login",  # tên hàm xử lý sau khi đăng nhập
    scope=["profile", "email"]
)
app.register_blueprint(google_bp, url_prefix="/login")


db = SQLAlchemy(app)
login = LoginManager(app)

cloudinary.config(
    cloud_name="dqpu49bbo",
    api_key="743773348627895",
    api_secret="EF7elKsibuI8JEBqfMNZYYWUYvo",
    secure=True
)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'phuongnam.it0212@gmail.com'
app.config['MAIL_PASSWORD'] = 'Phuongnam0212'

mail = Mail(app)

