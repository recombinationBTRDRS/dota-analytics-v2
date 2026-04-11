"""FastAPI application entry point.

Main application with:
- Health check endpoints
- CORS middleware
- Request logging middleware
- Structured logging
- Dependency injection for settings
- Error handlers
"""

import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.config import get_settings
from app.logging_config import get_logger, RequestContextMiddleware

# Get settings and logger
settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events (startup/shutdown)."""

    # =========================
    # STARTUP
    # =========================
    logger.info(
        "service_startup",
        service=settings.SERVICE_NAME,
        port=settings.SERVICE_PORT,
        debug=settings.DEBUG,
    )

    # Initialize database
    try:
        from app.db.mongodb import init_db, ensure_indexes

        db = await init_db()
        await ensure_indexes()

        logger.info("database_initialized")

    except Exception as exc:
        logger.error(
            "database_initialization_failed",
            error=str(exc),
            error_type=type(exc).__name__,
            exc_info=True,
        )
        raise

    yield

    # =========================
    # SHUTDOWN
    # =========================
    try:
        from app.db.mongodb import close_db

        await close_db()

        logger.info("database_closed")

    except Exception as exc:
        logger.error(
            "database_close_failed",
            error=str(exc),
            error_type=type(exc).__name__,
            exc_info=True,
        )

    logger.info(
        "service_shutdown",
        service=settings.SERVICE_NAME,
    )


# Initialize FastAPI app
app = FastAPI(
    title="Dota 2 Ingestion Service",
    version="1.0.0",
    description="Fetch, parse, validate, and store Dota 2 matches from OpenDota API",
    lifespan=lifespan,
    debug=settings.DEBUG,
)

# Add logging middleware
app.add_middleware(RequestContextMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)


# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    logger.debug("health_check_requested")
    return {
        "status": "ok",
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
        "debug": settings.DEBUG,
    }


@app.get("/ready", tags=["health"])
async def ready_check():
    """Readiness check endpoint."""
    logger.debug("readiness_check_requested")
    return {
        "ready": True,
        "service": settings.SERVICE_NAME,
        "port": settings.SERVICE_PORT,
    }


@app.get("/config", tags=["debug"])
async def get_config():
    """Get current configuration (debug endpoint)."""

    if not settings.DEBUG:
        logger.warning("config_endpoint_access_denied", reason="production_mode")
        return {"error": "Not available in production"}

    logger.info("config_endpoint_accessed")

    return {
        "service_name": settings.SERVICE_NAME,
        "service_port": settings.SERVICE_PORT,
        "log_level": settings.LOG_LEVEL,
        "opendota_api": settings.OPENDOTA_BASE_URL,
        "mongodb_db": settings.MONGODB_DB_NAME,
        "debug": settings.DEBUG,
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""

    request_id = str(uuid.uuid4())

    logger.error(
        "unhandled_exception",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        error=str(exc),
        error_type=type(exc).__name__,
        exc_info=True,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status": 500,
            "detail": str(exc) if settings.DEBUG else "An error occurred",
            "request_id": request_id,
        },
    )


# ============================================================================
# LOCAL RUN
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )