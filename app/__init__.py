from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote
app = Flask(__name__)
app.config['SECRET_KEY']='jikagfvcuyidwsgvvudbsjahfduyjfvdguieygvsfuy'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:%s@localhost/recruitmentdb?charset=utf8mb4' % quote("Admin@123")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config["PAGE_SIZE"] = 8

db = SQLAlchemy(app)
