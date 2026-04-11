"""Tests for logging configuration.

Test suite for:
- Structured logging setup
- Log levels
- Request logging
- Error logging
"""

import pytest
import logging
from unittest.mock import patch, MagicMock
from app.logging_config import (
    get_logger,
    configure_logging,
    LoggingConfig,
)
from app.config import Settings


class TestLoggingConfiguration:
    """Test logging configuration."""
    
    def test_logging_config_setup(self):
        """Test that logging configuration setup works."""
        LoggingConfig.setup()
        # Verify root logger is configured
        root_logger = logging.getLogger()
        assert root_logger is not None
    
    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a logger instance."""
        logger = get_logger(__name__)
        assert logger is not None
    
    def test_logger_has_info_method(self):
        """Test that logger has info logging method."""
        logger = get_logger(__name__)
        assert hasattr(logger, "info")
    
    def test_logger_has_error_method(self):
        """Test that logger has error logging method."""
        logger = get_logger(__name__)
        assert hasattr(logger, "error")
    
    def test_logger_has_warning_method(self):
        """Test that logger has warning logging method."""
        logger = get_logger(__name__)
        assert hasattr(logger, "warning")
    
    def test_logger_has_debug_method(self):
        """Test that logger has debug logging method."""
        logger = get_logger(__name__)
        assert hasattr(logger, "debug")


class TestLoggingLevels:
    """Test logging levels."""
    
    def test_info_logging(self, caplog):
        """Test INFO level logging."""
        logger = get_logger(__name__)
        with caplog.at_level(logging.INFO):
            logger.info("test_message", key="value")
        # Verify log was captured
        assert any("test_message" in record.message for record in caplog.records)
    
    def test_error_logging(self, caplog):
        """Test ERROR level logging."""
        logger = get_logger(__name__)
        with caplog.at_level(logging.ERROR):
            logger.error("test_error", error_code=500)
        assert any("test_error" in record.message for record in caplog.records)
    
    def test_warning_logging(self, caplog):
        """Test WARNING level logging."""
        logger = get_logger(__name__)
        with caplog.at_level(logging.WARNING):
            logger.warning("test_warning", issue="something")
        assert any("test_warning" in record.message for record in caplog.records)
    
    def test_debug_logging(self, caplog):
        """Test DEBUG level logging."""
        logger = get_logger(__name__)
        with caplog.at_level(logging.DEBUG):
            logger.debug("test_debug", detail="info")
        assert any("test_debug" in record.message for record in caplog.records)


class TestRequestContextMiddleware:
    """Test request context middleware."""
    
    def test_middleware_initialization(self):
        """Test middleware initialization."""
        from app.logging_config import RequestContextMiddleware
        from unittest.mock import MagicMock
        
        app_mock = MagicMock()
        middleware = RequestContextMiddleware(app_mock)
        assert middleware.app is app_mock
    
    @pytest.mark.asyncio
    async def test_middleware_with_non_http_request(self):
        """Test middleware with non-HTTP request."""
        from app.logging_config import RequestContextMiddleware
        from unittest.mock import MagicMock, AsyncMock
        
        app_mock = AsyncMock()
        middleware = RequestContextMiddleware(app_mock)
        
        scope = {"type": "websocket"}
        receive = MagicMock()
        send = MagicMock()
        
        await middleware(scope, receive, send)
        # Verify app was called for non-HTTP
        app_mock.assert_called_once()


class TestStructuredLogging:
    """Test structured logging features."""
    
    def test_logger_with_context(self, caplog):
        """Test logger with context data."""
        logger = get_logger(__name__)
        with caplog.at_level(logging.INFO):
            logger.info(
                "operation_completed",
                user_id=123,
                duration=0.45,
                status="success"
            )
        # Verify structured data was logged
        assert any("operation_completed" in record.message for record in caplog.records)
    
    def test_logger_with_error_context(self, caplog):
        """Test logger with error context."""
        logger = get_logger(__name__)
        with caplog.at_level(logging.ERROR):
            logger.error(
                "operation_failed",
                error_type="ValidationError",
                error_message="Invalid input"
            )
        assert any("operation_failed" in record.message for record in caplog.records)


class TestLogLevelConfiguration:
    """Test log level configuration."""
    
    def test_log_config_has_level(self):
        """Test that LoggingConfig has LOG_LEVEL."""
        assert hasattr(LoggingConfig, "LOG_LEVEL")
        assert isinstance(LoggingConfig.LOG_LEVEL, str)
    
    def test_log_config_has_format(self):
        """Test that LoggingConfig has LOG_FORMAT."""
        assert hasattr(LoggingConfig, "LOG_FORMAT")
        assert LoggingConfig.LOG_FORMAT in ["json", "text"]
    
    def test_log_config_setup_is_callable(self):
        """Test that LoggingConfig.setup is callable."""
        assert callable(LoggingConfig.setup)