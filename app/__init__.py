from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
import sqlalchemy as sa

login_manager = LoginManager()
db = SQLAlchemy()
migrate = Migrate()

def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from app.routes import main
    app.register_blueprint(main)

    @app.shell_context_processor
    def make_shell_context():
        from app.models import User
        return {
            "db": db,
            "User": User,
            "sa": sa,
        }

    return app
