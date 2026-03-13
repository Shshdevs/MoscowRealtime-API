import logging
import time
from flask import request, g


logger = logging.getLogger(__name__)


def register_middlewares(app):

    @app.before_request
    def start_timer():
        g.start_time = time.time()

    @app.after_request
    def log_request(response):

        duration = time.time() - g.start_time

        logger.info(
            "%s %s %s %s %.3fs",
            request.remote_addr,
            request.method,
            request.path,
            response.status_code,
            duration,
        )

        return response
