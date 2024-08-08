from flask import Flask
from flask_login import LoginManager
app = Flask(__name__)
app.config.from_object('config')

import psycopg2

# Функция для установки соединения с PostgreSQL
def get_db():
    conn = psycopg2.connect(
        host=app.config['DB_HOST'],
        port=app.config['DB_PORT'],
        user=app.config['DB_USER'],
        password=app.config['DB_PASSWORD'],
        database=app.config['DB_NAME']
    )
    return conn
login = LoginManager(app)
login.login_view = 'login'
from app import views

