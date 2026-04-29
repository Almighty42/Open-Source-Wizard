from flask import Blueprint

project_bp = Blueprint("project", __name__, url_prefix="/projects")

from . import routes
