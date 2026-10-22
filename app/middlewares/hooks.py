import time
import uuid
from flask import g, request


def register_hooks(app):
    @app.before_request
    def before_request():
        g.request_id = uuid.uuid4().hex[:8]
        g.start_time = time.time()

    @app.after_request
    def after_request(response):
        if request.path.startswith("/static"):
            return response

        start_time = g.get("start_time")
        if start_time is not None:
            duration = f"{(time.time() - start_time) * 1000:.0f}ms"
        else:
            duration = "-"

        app.logger.info(
            "%s %s %s — %s [%s]",
            request.method,
            request.path,
            response.status_code,
            duration,
            g.get("request_id", "-"),
        )
        return response
