from flask import render_template
from . import errors_bp

@errors_bp.app_errorhandler(404)
def not_found(e):
    return render_template("errors/404.html"), 404

@errors_bp.app_errorhandler(429)
def too_many_requests(e):
    return render_template("errors/429.html"), 429

@errors_bp.app_errorhandler(500)
def server_error(e):
    return render_template("errors/500.html"), 500
