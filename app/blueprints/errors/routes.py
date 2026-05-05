from flask import render_template
from . import errors_bp

@errors_bp.app_errorhandler(404)
def not_found(e):
    return render_template(
            "errors/404.html",
            title="404"
            ), 404

@errors_bp.app_errorhandler(429)
def too_many_requests(e):
    return render_template(
                "errors/429.html",
                title="429",
                           ), 429

@errors_bp.app_errorhandler(500)
def server_error(e):
    return render_template(
            "errors/500.html",
            title="500",
            ), 500
