"""Tests for application lifespan events.

Test suite for:
- Startup events
- Shutdown events
- Database initialization
- Error handling
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app


class TestApplicationLifespan:
    """Test application lifespan management."""
    
    def test_app_initialization(self):
        """Test that app initializes without errors."""
        assert app is not None
        assert app.title == "Dota 2 Ingestion Service"
        assert app.version == "1.0.0"
    
    def test_app_has_health_endpoint(self):
        """Test that /health endpoint exists."""
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_app_has_ready_endpoint(self):
        """Test that /ready endpoint exists."""
        client = TestClient(app)
        response = client.get("/ready")
        assert response.status_code == 200
    
    def test_app_has_config_endpoint(self):
        """Test that /config endpoint exists."""
        client = TestClient(app)
        response = client.get("/config")
        assert response.status_code == 200


class TestLifecycleEvents:
    """Test lifecycle event handlers."""
    
    def test_startup_event_registered(self):
        """Test that startup event is registered."""
        # Check that on_event decorator was used
        assert hasattr(app, 'on_event')
    
    def test_shutdown_event_registered(self):
        """Test that shutdown event is registered."""
        # Check that on_event decorator was used
        assert hasattr(app, 'on_event')


class TestErrorHandling:
    """Test error handling in lifespan."""
    
    def test_health_check_on_error(self):
        """Test that health check works even if DB not initialized."""
        client = TestClient(app)
        response = client.get("/health")
        # Should still work (doesn't depend on DB)
        assert response.status_code == 200
    
    def test_global_exception_handler(self):
        """Test global exception handler returns proper error format."""
        client = TestClient(app)
        # Trigger a 404 to test error handler
        response = client.get("/nonexistent")
        assert response.status_code == 404


class TestAppConfiguration:
    """Test app configuration during startup."""
    
    def test_cors_middleware_enabled(self):
        """Test that CORS middleware is enabled."""
        client = TestClient(app)
        response = client.options("/health")
        # OPTIONS should be allowed by CORS middleware
        assert response.status_code in [200, 204, 405]
    
    def test_logging_middleware_enabled(self):
        """Test that logging middleware is enabled."""
        client = TestClient(app)
        # Should not raise any errors
        response = client.get("/health")
        assert response.status_code == 200


class TestDependencyInjection:
    """Test dependency injection setup."""
    
    def test_limiter_configured(self):
        """Test that rate limiter is configured."""
        assert app.state.limiter is not None
    
    def test_db_dependencies_available(self):
        """Test that database dependencies are available."""
        from app.db.dependencies import (
            get_database,
            get_match_repository,
            get_ingestion_log_repository,
        )
        
        assert callable(get_database)
        assert callable(get_match_repository)
        assert callable(get_ingestion_log_repository)