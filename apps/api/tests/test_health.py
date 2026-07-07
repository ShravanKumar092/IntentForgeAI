from fastapi.testclient import TestClient

from intentforge_api.main import app


client = TestClient(app)


def test_health_check_returns_healthy_service() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "healthy"
    assert payload["service"] == "intentforge-api"
    assert payload["version"] == "0.1.0"
    assert "timestamp" in payload


def test_health_check_matches_expected_contract() -> None:
    response = client.get("/api/v1/health")
    payload = response.json()

    assert set(payload) == {
        "status",
        "service",
        "version",
        "timestamp",
    }