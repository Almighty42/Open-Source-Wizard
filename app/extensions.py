from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

login_manager.session_protection = "strong"

@login_manager.user_loader
def load_user(id):
    from app.models.auth import User
    return db.session.get(User, int(id))
