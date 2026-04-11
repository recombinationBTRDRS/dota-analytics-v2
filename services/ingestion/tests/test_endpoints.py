"""Tests for API endpoints.

Test suite for:
- Ingestion endpoints
- Request/Response validation
- Error handling
- HTTP status codes
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_health_endpoint_200(self, client):
        """Test /health returns 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "ingestion"
        assert data["version"] == "1.0.0"
    
    def test_ready_endpoint_200(self, client):
        """Test /ready returns 200 OK."""
        response = client.get("/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["ready"] is True
        assert data["service"] == "ingestion"


class TestIngestEndpoints:
    """Test ingestion endpoints."""
    
    def test_ingest_opendota_202(self, client):
        """Test POST /ingest/opendota returns 202 Accepted."""
        response = client.post(
            "/api/v1/ingest/opendota",
            json={"match_id": 7123456789}
        )
        assert response.status_code == 202
        data = response.json()
        assert data["match_id"] == 7123456789
        assert data["status"] == "pending"
        assert data["request_id"] is not None
    
    def test_ingest_opendota_invalid_match_id(self, client):
        """Test POST /ingest/opendota with invalid match_id."""
        response = client.post(
            "/api/v1/ingest/opendota",
            json={"match_id": -1}  # Invalid: must be > 0
        )
        assert response.status_code == 422  # Validation error
    
    def test_ingest_opendota_missing_match_id(self, client):
        """Test POST /ingest/opendota without match_id."""
        response = client.post(
            "/api/v1/ingest/opendota",
            json={}
        )
        assert response.status_code == 422  # Validation error
    
    def test_ingest_status_200(self, client):
        """Test GET /ingest/status/{match_id}."""
        response = client.get("/api/v1/ingest/status/7123456789")
        assert response.status_code == 200
        data = response.json()
        assert data["match_id"] == 7123456789
        assert "status" in data
        assert "attempt" in data


class TestConfigEndpoint:
    """Test config debug endpoint."""
    
    def test_config_endpoint_in_debug(self, client):
        """Test /config endpoint in debug mode."""
        response = client.get("/config")
        assert response.status_code == 200
        data = response.json()
        assert "service_name" in data
        assert data["service_name"] == "ingestion"


class TestErrorHandling:
    """Test error handling."""
    
    def test_404_not_found(self, client):
        """Test 404 Not Found for non-existent endpoint."""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """Test 405 Method Not Allowed."""
        response = client.delete("/health")
        assert response.status_code == 405


class TestAPIVersioning:
    """Test API versioning."""
    
    def test_api_v1_prefix(self, client):
        """Test that endpoints use /api/v1/ prefix."""
        response = client.post(
            "/api/v1/ingest/opendota",
            json={"match_id": 7123456789}
        )
        assert response.status_code == 202
    
    def test_unversioned_endpoint_not_found(self, client):
        """Test that unversioned endpoints return 404."""
        response = client.post(
            "/ingest/opendota",
            json={"match_id": 7123456789}
        )
        assert response.status_code == 404