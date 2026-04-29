from app.blueprints.main import main_bp
from app.blueprints.auth import auth_bp
from app.blueprints.articles import article_bp
from app.blueprints.projects import project_bp

__all__ = [
        "main_bp",
        "auth_bp",
        "article_bp",
        "project_bp"
]
