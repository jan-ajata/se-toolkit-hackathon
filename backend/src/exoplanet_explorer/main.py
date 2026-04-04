"""Exoplanet Explorer — FastAPI application."""

import logging
import time
import traceback

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from exoplanet_explorer.auth import verify_api_key
from exoplanet_explorer.routers import exoplanets
from exoplanet_explorer.settings import settings

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    logging.getLogger("uvicorn.access").propagate = True

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        description="Browse, filter, and calculate survival metrics for confirmed exoplanets.",
        version="0.1.0",
    )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        """Return error details in the response for easier debugging."""
        tb = traceback.format_exception(type(exc), exc, exc.__traceback__)
        logger.exception(
            "unhandled_exception",
            extra={"event": "unhandled_exception", "path": request.url.path},
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail": str(exc),
                "type": type(exc).__name__,
                "path": request.url.path,
                "traceback": tb[-3:],
            },
        )

    @app.middleware("http")
    async def log_requests(
        request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        logger.info(
            "request_started",
            extra={
                "event": "request_started",
                "method": request.method,
                "path": request.url.path,
            },
        )
        t0 = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - t0) * 1000)
        level = logging.ERROR if response.status_code >= 500 else logging.INFO
        logger.log(
            level,
            "request_completed",
            extra={
                "event": "request_completed",
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(
        exoplanets.router,
        prefix="/exoplanets",
        tags=["exoplanets"],
        dependencies=[Depends(verify_api_key)],
    )

    return app


app = create_app()
