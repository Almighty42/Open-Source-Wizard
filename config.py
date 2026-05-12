import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()

class Config:
    APP_NAME = "Open Source Wizard"
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ('1', 'true', 'yes')
    TESTING = os.environ.get('TESTING', 'False').lower() in ('1', 'true', 'yes')
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")

    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 3001))
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            'sqlite:///' + os.path.join(basedir, 'app.db')

    REMEMBER_COOKIE_DURATION = timedelta(hours=1)
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"

    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


config = Config()
