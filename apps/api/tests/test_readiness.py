from uuid import uuid4

from fastapi.testclient import TestClient

from intentforge_api.core.config import Settings
from intentforge_api.core.correlation import CORRELATION_ID_HEADER
from intentforge_api.db.connection import DatabaseConnectivityError
from intentforge_api.main import create_app


def create_test_client() -> TestClient:
    settings = Settings(_env_file=None, app_environment="testing", app_debug=False)
    return TestClient(create_app(settings))


def test_readiness_returns_ready_when_database_probe_succeeds(monkeypatch) -> None:
    client = create_test_client()
    supplied_correlation_id = str(uuid4())

    async def fake_probe(engine) -> None:
        return None

    monkeypatch.setattr("intentforge_api.api.routes.readiness.probe_database_connection", fake_probe)

    response = client.get(
        "/api/v1/readiness",
        headers={CORRELATION_ID_HEADER: supplied_correlation_id},
    )

    assert response.status_code == 200
    assert response.headers[CORRELATION_ID_HEADER] == supplied_correlation_id

    payload = response.json()

    assert payload["status"] == "ready"
    assert payload["database"] == "available"
    assert "timestamp" in payload


def test_readiness_returns_controlled_unavailable_response(monkeypatch) -> None:
    client = create_test_client()

    async def fake_probe(engine) -> None:
        raise DatabaseConnectivityError("database connectivity check failed")

    monkeypatch.setattr("intentforge_api.api.routes.readiness.probe_database_connection", fake_probe)

    response = client.get("/api/v1/readiness")

    assert response.status_code == 503

    payload = response.json()

    assert payload["status"] == "unavailable"
    assert payload["database"] == "unavailable"
    assert "timestamp" in payload


def test_health_endpoint_remains_independent_of_database_availability(monkeypatch) -> None:
    client = create_test_client()

    async def fake_probe(engine) -> None:
        raise DatabaseConnectivityError("database connectivity check failed")

    monkeypatch.setattr("intentforge_api.api.routes.readiness.probe_database_connection", fake_probe)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
