from flask import Flask
from config import Config
from app.extensions import db, login_manager, migrate
from scripts.seed import seed_bp
from app.blueprints import main_bp, auth_bp, article_bp, project_bp, errors_bp
from app.extensions import limiter

import sqlalchemy as sa

def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(article_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(errors_bp)
    app.register_blueprint(seed_bp)

    @app.shell_context_processor
    def make_shell_context():
        from app.models import User
        admin_username = app.config.get("ADMIN_USERNAME")
        return {
            "db": db,
            "sa": sa,
            "User": User,
            "admin": db.session.scalar(sa.select(User).where(User.username == admin_username))
        }

    return app
