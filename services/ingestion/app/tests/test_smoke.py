import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path


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
