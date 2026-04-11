"""FastAPI application entry point.

Main application with:
- Health check endpoints
- CORS middleware
- Dependency injection for settings
- Error handlers
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Aplication lifespan events (startup/shutdown).

    Startup: Initialize connections
    Shutdown: Close connections
    """
    #STARTUP
    print(f"🚀 {settings.SERVICE_NAME} service starting on port {settings.SERVICE_PORT}")
    yield
    #SHUTDOWN
    print(f"🛑 {settings.SERVICE_NAME} service shutting down")

# Initialize FastAPI app
app = FastAPI(
    title="Dota 2 Ingestion Service",
    version="1.0.0",
    description="Fetch, parse, validate and store Dota 2 matches from Open Dota API",
    lifespan=lifespan,
    debug=settings.DEBUG,
)

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
    """Health check endpoint.

    Returns:
        dict: Service status
    """
    return {
        "status": "ok",
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
        "debug": settings.DEBUG,
    }

@app.get("/ready", tags=["health"])
async def ready_check():
    """Readiness check endpoint.
    
    Checks if service is ready to accept requests.
    In future: check database connections, cache, etc.
    
    Returns:
        dict: Readiness status
    """
    return {
        "ready": True,
        "service": settings.SERVICE_NAME,
        "port": settings.SERVICE_PORT,
    }


@app.get("/config", tags=["debug"])
async def get_config():
    """Get current configuration (debug endpoint).
    
    ⚠️ Only available in DEBUG mode
    
    Returns:
        dict: Current settings (without sensitive data)
    """
    if not settings.DEBUG:
        return {"error": "Not available in production"}
    
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
async def global_exception_handler(request, exc):
    """Global exception handler.
    
    Args:
        request: HTTP request
        exc: Exception that occurred
        
    Returns:
        JSONResponse with error details
    """
    return {
        "error": "Internal server error",
        "status": 500,
        "detail": str(exc) if settings.DEBUG else "An error occurred"
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )