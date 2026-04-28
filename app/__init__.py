from flask import Flask
from config import Config
import sqlalchemy as sa
from app.extensions import db, login_manager, migrate
from scripts.seed import seed_bp

def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from app.routes import main
    app.register_blueprint(main)
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
