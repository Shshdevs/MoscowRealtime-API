import logging

import uvicorn

from app.shared.config import Settings
from app.shared.logging import setup_logging
from app.api.app import create_app


setup_logging()
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting application")

    settings = Settings.from_env()
    app = create_app(settings)

    logger.info(
        "Starting HTTP server on %s:%s",
        settings.host,
        settings.port,
    )

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        proxy_headers=True,
        forwarded_allow_ips=settings.forwarded_allow_ips,
    )


if __name__ == "__main__":
    main()
