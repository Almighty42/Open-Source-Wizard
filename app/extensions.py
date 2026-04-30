from flask import url_for, redirect
from flask_limiter.util import get_remote_address

from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

login_manager.session_protection = "strong"

limiter = Limiter(
        get_remote_address,
        default_limits=["3/second", "200 per day", "75 per hour"],
        storage_uri="memory://",
)

@login_manager.user_loader
def load_user(id):
    from app.models.auth import User
    return db.session.get(User, int(id))

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for("main.index"))
