from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to Pandada.AI API"
    assert data["version"] == "0.1.0"
    assert "docs" in data
    assert "redoc" in data


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "pandada-backend"
    assert data["version"] == "0.1.0"
