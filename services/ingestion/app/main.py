"""FastAPI application entry point.

Main application with:
- Proper lifespan management with DB initialization
- Database initialization/cleanup
- Health check endpoints
- CORS middleware
- Request logging middleware
- Structured logging
- Dependency injection
- Error handlers with proper HTTP status codes
- API routing
"""

import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import get_settings
from app.logging_config import get_logger, RequestContextMiddleware
from app.db.mongodb import init_db, close_db, ensure_indexes
from app.routers import ingest
from app.schemas import HealthResponse, ReadyResponse, ErrorDetail

# Get settings and logger
settings = get_settings()
logger = get_logger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager.
    
    Handles:
    - Startup: Database initialization, index creation
    - Shutdown: Graceful database closure
    """
    
    # ========================================================================
    # STARTUP
    # ========================================================================
    logger.info(
        "service_startup_beginning",
        service=settings.SERVICE_NAME,
        port=settings.SERVICE_PORT,
        debug=settings.DEBUG,
        log_level=settings.LOG_LEVEL,
    )
    
    try:
        # Initialize database
        logger.info("database_initialization_starting")
        db = await init_db()
        logger.info("database_connection_established")
        
        # Create indexes
        logger.info("database_indexes_creation_starting")
        await ensure_indexes()
        logger.info("database_indexes_created_successfully")
        
        # Log startup success
        logger.info(
            "service_startup_completed",
            service=settings.SERVICE_NAME,
            port=settings.SERVICE_PORT,
            status="ready",
        )
    
    except Exception as exc:
        logger.error(
            "service_startup_failed",
            error=str(exc),
            error_type=type(exc).__name__,
            exc_info=True,
        )
        # Re-raise to prevent app from starting
        raise
    
    # Yield control to FastAPI (app is now running)
    yield
    
    # ========================================================================
    # SHUTDOWN
    # ========================================================================
    logger.info("service_shutdown_beginning", service=settings.SERVICE_NAME)
    
    try:
        # Close database connections
        logger.info("database_connection_closing")
        await close_db()
        logger.info("database_connection_closed_successfully")
        
        # Log shutdown success
        logger.info(
            "service_shutdown_completed",
            service=settings.SERVICE_NAME,
            status="stopped",
        )
    
    except Exception as exc:
        logger.error(
            "service_shutdown_error",
            error=str(exc),
            error_type=type(exc).__name__,
            exc_info=True,
        )


# Initialize FastAPI app
app = FastAPI(
    title="Dota 2 Ingestion Service",
    version="1.0.0",
    description="Fetch, parse, validate, and store Dota 2 matches from OpenDota API",
    lifespan=lifespan,
    debug=settings.DEBUG,
)

# Add rate limiter to app
app.state.limiter = limiter

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

@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Health check endpoint.
    
    Returns:
        HealthResponse with service status
    """
    logger.debug("health_check_requested")
    return HealthResponse(
        status="ok",
        service=settings.SERVICE_NAME,
        version="1.0.0",
        debug=settings.DEBUG,
    )


@app.get("/ready", response_model=ReadyResponse, tags=["health"])
async def ready_check():
    """Readiness check endpoint.
    
    Checks if service is ready to accept requests.
    
    Returns:
        ReadyResponse with readiness status
    """
    logger.debug("readiness_check_requested")
    return ReadyResponse(
        ready=True,
        service=settings.SERVICE_NAME,
        port=settings.SERVICE_PORT,
    )


@app.get("/config", tags=["debug"])
async def get_config():
    """Get current configuration (debug endpoint).
    
    ⚠️ Only available in DEBUG mode
    
    Returns:
        Configuration object
    """
    if not settings.DEBUG:
        logger.warning("config_endpoint_access_denied", reason="production_mode")
        return {"error": "Not available in production"}
    
    logger.info("config_endpoint_accessed")
    return {
        "service_name": settings.SERVICE_NAME,
        "service_port": settings.SERVICE_PORT,
        "log_level": settings.LOG_LEVEL,
        "log_format": settings.LOG_FORMAT,
        "opendota_api": settings.OPENDOTA_BASE_URL,
        "mongodb_db": settings.MONGODB_DB_NAME,
        "redis_url": "redis://***",  # Sanitize for logging
        "debug": settings.DEBUG,
    }


# ============================================================================
# API ROUTERS
# ============================================================================

app.include_router(ingest.router)


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler.
    
    Catches all unhandled exceptions and returns proper HTTP 500 response.
    
    Args:
        request: HTTP request
        exc: Exception that occurred
        
    Returns:
        JSONResponse with error details and HTTP 500 status
    """
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
    
    error_detail = ErrorDetail(
        error="Internal server error",
        status=500,
        detail=str(exc) if settings.DEBUG else "An error occurred",
        request_id=request_id,
    )
    
    return JSONResponse(
        status_code=500,
        content=error_detail.model_dump(),
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )