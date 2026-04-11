"""Tests for Docker and containerization.

Test suite for:
- Health check endpoints
- Container configuration
- Service availability
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
async def async_client():
    """Create asynchronous test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


class TestHealthCheck:
    """Tests for health check endpoints."""

    @pytest.mark.asyncio
    async def test_health_endpoint(self, async_client):
        """Test /health endpoint."""
        response = await async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "ingestion"
        assert "version" in data

    @pytest.mark.asyncio
    async def test_ready_endpoint(self, async_client):
        """Test /ready endpoint."""
        response = await async_client.get("/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["ready"] is True


class TestConfigEndpoint:
    """Tests for configuration debug endpoint."""

    @pytest.mark.asyncio
    async def test_config_endpoint_debug_mode(self, async_client):
        """Test /config endpoint in debug mode."""
        response = await async_client.get("/config")
        assert response.status_code == 200
        data = response.json()
        assert "service_name" in data
        assert "service_port" in data