from flask import render_template, request, g
from . import errors_bp

import logging
logger = logging.getLogger(__name__)

@errors_bp.app_errorhandler(404)
def not_found(e):
    logger.warning("404: %s", request.path) 
    return render_template("errors/404.html", title="404"), 404

@errors_bp.app_errorhandler(429)
def too_many_requests(e):
    logger.warning("429: %s", request.path)
    return render_template("errors/429.html", title="429"), 429

@errors_bp.app_errorhandler(500)
def server_error(e):
    logger.error("500 on %s [%s]: %s", request.path, g.get("request_id", "—"), str(e), exc_info=True)
    return render_template("errors/500.html", title="500"), 500
