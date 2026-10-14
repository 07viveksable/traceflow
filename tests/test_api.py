from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home_endpoint():
    """Check whether the home endpoint is working."""
    response = client.get("/")

    assert response.status_code == 200


def test_health_endpoint():
    """Check whether the health endpoint is working."""
    response = client.get("/health")

    assert response.status_code == 200


def test_performance_analytics_requires_authentication():
    """Check that analytics is protected from unauthenticated requests."""
    response = client.get("/performance/analytics")

    assert response.status_code == 401