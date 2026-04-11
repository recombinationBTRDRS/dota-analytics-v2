"""Logging configuration using structlog.

Provides structured JSON logging with:
- JSON output format
- Request/Response tracking
- Error tracking
- Custom context injection
"""

import logging
import logging.config
import structlog
from typing import Any, Dict
from pythonjsonlogger import jsonlogger
from app.config import get_settings


# Get settings
settings = get_settings()


def configure_logging() -> None:
    """Configure structured logging with structlog and JSON output.
    
    Sets up:
    - structlog for structured logging
    - JSON formatting for all logs
    - Proper log levels
    - Request tracking
    """
    
    # Configure standard logging first
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": jsonlogger.JsonFormatter,
                "format": (
                    "%(timestamp)s %(level)s %(name)s "
                    "%(message)s %(pathname)s %(lineno)d"
                ),
            },
            "standard": {
                "format": "[%(levelname)s] %(name)s - %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.LOG_LEVEL,
                "formatter": settings.LOG_FORMAT,
                "stream": "ext://sys.stdout",
            },
        },
        "root": {
            "level": settings.LOG_LEVEL,
            "handlers": ["console"],
        },
    })
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,            
            structlog.processors.JSONRenderer()
            if settings.LOG_FORMAT == "json"
            else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        BoundLogger instance with context
        
    Example:
        logger = get_logger(__name__)
        logger.info("operation_completed", user_id=123, duration=0.45)
    """
    return structlog.get_logger(name)


class RequestContextMiddleware:
    """Middleware to add request context to logs.
    
    Adds:
    - Request ID
    - Request method and path
    - Client IP
    - User agent
    """
    
    def __init__(self, app):
        """Initialize middleware.
        
        Args:
            app: FastAPI app instance
        """
        self.app = app
    
    async def __call__(self, scope, receive, send):
        """ASGI middleware handler.
        
        Args:
            scope: ASGI scope
            receive: ASGI receive channel
            send: ASGI send channel
        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Extract request info
        method = scope.get("method", "UNKNOWN")
        path = scope.get("path", "UNKNOWN")
        client_ip = scope.get("client", ("unknown", 0))[0]
        headers = dict(scope.get("headers", []))
        user_agent = headers.get(b"user-agent", b"unknown").decode("utf-8", errors="ignore")
        
        # Bind context to logger
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            method=method,
            path=path,
            client_ip=client_ip,
            user_agent=user_agent,
        )
        
        logger = get_logger(__name__)
        logger.info("request_started", method=method, path=path)
        
        async def send_wrapper(message):
            """Wrap send to log response."""
            if message["type"] == "http.response.start":
                status = message.get("status", 500)
                logger.info("request_completed", status=status, method=method, path=path)
            await send(message)
        
        await self.app(scope, receive, send_wrapper)


class LoggingConfig:
    """Configuration class for logging settings."""
    
    LOG_LEVEL: str = settings.LOG_LEVEL
    LOG_FORMAT: str = settings.LOG_FORMAT
    
    @staticmethod
    def setup() -> None:
        """Set up logging configuration."""
        configure_logging()


# Initialize on import
LoggingConfig.setup()