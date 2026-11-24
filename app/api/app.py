import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.container import ApplicationContainer, build_container
from app.api.routes.analysis import router as analysis_router
from app.api.routes.events import router as events_router
from app.api.routes.location import router as location_router
from app.infrastructure.firebase.listeners.collection_listener import CollectionListener
from app.infrastructure.firebase.search.search_indexer import SearchIndexer
from app.infrastructure.firebase.search.search_prefix_builder import SearchPrefixBuilder
from app.shared.config import Settings
from app.shared.constants import FIRESTORE_COLLECTIONS

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        container: ApplicationContainer = app.state.container
        builder = SearchPrefixBuilder()
        listeners = []
        try:
            for collection_name in FIRESTORE_COLLECTIONS:
                indexer = SearchIndexer(
                    db=container["db"],
                    builder=builder,
                    collection_name=collection_name,
                )
                listener = CollectionListener(indexer=indexer)
                listener.start()
                listeners.append(listener)
                logger.info("Started listener for collection: %s", collection_name)
            yield
        finally:
            try:
                container["events_data_source"].close()
            except Exception:
                logger.exception("Failed to close events data source")
            for listener in reversed(listeners):
                try:
                    listener.stop()
                except Exception:
                    logger.exception("Failed to stop Firestore listener")

    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.state.settings = settings
    app.state.container = build_container(settings)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_allowed_origins),
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "Authorization"],
    )

    @app.middleware("http")
    async def log_request(request: Request, call_next):
        started_at = time.time()
        response = await call_next(request)
        logger.info(
            "%s %s %s %s %.3fs",
            request.client.host if request.client else None,
            request.method,
            request.url.path,
            response.status_code,
            time.time() - started_at,
        )
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        return JSONResponse({"success": False, "error": "Bad request"}, status_code=400)

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(request: Request, exc: StarletteHTTPException):
        messages = {
            404: "Endpoint not found",
            413: "File too large",
            429: "Too many requests",
        }
        return JSONResponse(
            {"success": False, "error": messages.get(exc.status_code, str(exc.detail))},
            status_code=exc.status_code,
        )

    @app.exception_handler(Exception)
    async def internal_error_handler(request: Request, exc: Exception):
        logger.error(
            "Unhandled request error: %s %s",
            request.method,
            request.url.path,
            exc_info=(type(exc), exc, exc.__traceback__),
        )
        return JSONResponse(
            {"success": False, "error": "Internal server error"}, status_code=500
        )

    @app.get("/api/health")
    async def health_check():
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
        }

    app.include_router(location_router, prefix="/api")
    app.include_router(analysis_router, prefix="/api")
    app.include_router(events_router, prefix="/api")
    return app
