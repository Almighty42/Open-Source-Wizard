from flask import Flask
from app.middlewares.hooks import register_hooks
from config import Config
from app.extensions import db, login_manager, migrate, limiter
from scripts.seed import seed_bp
from app.blueprints import main_bp, auth_bp, article_bp, project_bp, errors_bp, admin_bp, api_bp
from app.filters import register_filters
from app.utils import inline_svg

import logging
import logging.config
import os
from dotenv import load_dotenv

import sqlalchemy as sa

def create_app(config=Config):
    configure_logging()

    app = Flask(__name__)
    app.config.from_object(config)

    app.add_url_rule(
        "/favicon.ico",
        endpoint="favicon",
        redirect_to="/static/favicon.ico",
    )

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    app.jinja_env.globals["inline_svg"] = inline_svg

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(article_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(errors_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(seed_bp)

    register_filters(app)

    @app.shell_context_processor
    def make_shell_context():
        from app.models import User
        admin_username = app.config.get("ADMIN_USERNAME")
        return {
            "db": db,
            "sa": sa,
            "User": User,
            "admin": db.session.scalar(
                sa.select(User).where(User.username == admin_username)
            ),
        }

    register_hooks(app)
    return app

def configure_logging():
    log_dir = os.getenv("LOG_DIR", "logs")
    os.makedirs(log_dir, exist_ok=True)

    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "loggers": {
            "werkzeug": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
            "MARKDOWN": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
        },
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "[%(asctime)s] %(levelname)s %(name)s %(module)s:%(lineno)d: %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "app_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "detailed",
                "filename": f"{log_dir}/app.log",
                "maxBytes": 10_485_760,  # 10MB
                "backupCount": 5,
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "detailed",
                "filename": f"{log_dir}/error.log",
                "maxBytes": 10_485_760,
                "backupCount": 5,
                "level": "ERROR",
            },
        },
        "root": {
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "handlers": ["console", "app_file", "error_file"],
        },
    })
