from flask import Blueprint

article_bp = Blueprint("article", __name__, url_prefix="/articles")

from . import routes
