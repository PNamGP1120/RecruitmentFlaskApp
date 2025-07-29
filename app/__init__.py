import cloudinary
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote
from flask_login import LoginManager
from flask_socketio import SocketIO
import eventlet
eventlet.monkey_patch()

# Set your message queue URI
MESSAGE_QUEUE = 'redis://localhost:6379'
app = Flask(__name__)
app.config['SECRET_KEY']='jikagfvcuyidwsgvvudbsjahfduyjfvdguieygvsfuy'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:%s@localhost/recruitmentdb?charset=utf8mb4' % quote("Admin@123")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config["PAGE_SIZE"] = 8

db = SQLAlchemy(app)
login = LoginManager(app)
# UPDATE THIS LINE: Add message_queue and set async_mode
socketio = SocketIO(app, async_mode='eventlet', message_queue=MESSAGE_QUEUE)

cloudinary.config(
    cloud_name="dqpu49bbo",
    api_key="743773348627895",
    api_secret="EF7elKsibuI8JEBqfMNZYYWUYvo",
    secure=True
)
