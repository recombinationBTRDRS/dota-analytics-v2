import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
from app.config import get_settings


# Add parent directiry to patch
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "ingestion"

def test_ready_endpoint(client):
    """"Test ready check endpoint"""
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["ready"] is True
    assert response.json()["service"] == "ingestion"    

def test_config_in_health_endpoint(client):
    """Test that health endpoint includes config info."""
    settings = get_settings()
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == settings.SERVICE_NAME
    assert data["debug"] == settings.DEBUG


class TestDatabaseIntegration:
    """Test database integration."""
    
    def test_app_startup_completes(self):
        """Test that app startup completes successfully."""
        client = TestClient(app)
        # App should be running without errors
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_ready_check_after_startup(self):
        """Test that service reports ready after startup."""
        client = TestClient(app)
        response = client.get("/ready")
        assert response.status_code == 200
        assert response.json()["ready"] is True


class TestAPIGateway:
    """Test API Gateway functionality."""
    
    def test_api_v1_routing(self):
        """Test that API routes to /api/v1/*."""
        client = TestClient(app)
        response = client.post(
            "/api/v1/ingest/opendota",
            json={"match_id": 7123456789}
        )
        assert response.status_code == 202
    
    def test_openapi_documentation(self):
        """Test that OpenAPI documentation is available."""
        client = TestClient(app)
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert data["info"]["title"] == "Dota 2 Ingestion Service"
        assert data["info"]["version"] == "1.0.0"