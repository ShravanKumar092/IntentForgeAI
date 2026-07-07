from fastapi.testclient import TestClient

from intentforge_api.core.config import Settings
from intentforge_api.main import create_app


def create_test_client() -> TestClient:
    settings = Settings(
        _env_file=None,
        app_name="IntentForge Test API",
        app_version="0.1.0-test",
        app_environment="testing",
        app_debug=False,
    )

    return TestClient(create_app(settings))


def test_health_check_returns_runtime_identity() -> None:
    client = create_test_client()

    response = client.get("/api/v1/health")

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "healthy"
    assert payload["service"] == "IntentForge Test API"
    assert payload["version"] == "0.1.0-test"
    assert payload["environment"] == "testing"
    assert payload["debug"] is False
    assert "timestamp" in payload


def test_health_check_matches_expected_contract() -> None:
    client = create_test_client()

    response = client.get("/api/v1/health")
    payload = response.json()

    assert set(payload) == {
        "status",
        "service",
        "version",
        "environment",
        "debug",
        "timestamp",
    }


def test_application_metadata_comes_from_settings() -> None:
    settings = Settings(
        _env_file=None,
        app_name="Configured IntentForge",
        app_version="2.5.0",
        app_environment="testing",
        app_debug=False,
    )

    app = create_app(settings)

    assert app.title == "Configured IntentForge"
    assert app.version == "2.5.0"
    assert app.debug is False
    assert app.state.settings is settings
    assert app.state.runtime_identity.application == "Configured IntentForge"