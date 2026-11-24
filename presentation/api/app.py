import logging
import time
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from config import Config
from container import build_container
from presentation.api.routes.analysis import router as analysis_router
from presentation.api.routes.location import router as location_router

logger = logging.getLogger(__name__)


def create_app():
    app = FastAPI()
    app.state.container = build_container()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
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
        messages = {404: "Endpoint not found", 413: "File too large", 429: "Too many requests"}
        return JSONResponse(
            {"success": False, "error": messages.get(exc.status_code, str(exc.detail))},
            status_code=exc.status_code,
        )

    @app.exception_handler(Exception)
    async def internal_error_handler(request: Request, exc: Exception):
        return JSONResponse({"success": False, "error": "Internal server error"}, status_code=500)

    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
        }

    app.include_router(location_router)
    app.include_router(analysis_router)
    return app
