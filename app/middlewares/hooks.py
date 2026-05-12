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
        duration_ms = round((time.time() - g.start_time) * 1000, 2)
        app.logger.info(
            "%s %s %s — %dms [%s]",
            request.method,
            request.path,
            response.status_code,
            duration_ms,
            g.request_id,
        )
        return response
