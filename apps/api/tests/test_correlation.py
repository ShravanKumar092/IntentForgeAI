from uuid import UUID, uuid4

from fastapi import Request
from fastapi.testclient import TestClient

from intentforge_api.core.config import Settings
from intentforge_api.core.correlation import (
    CORRELATION_ID_HEADER,
    get_correlation_id,
)
from intentforge_api.main import create_app


def create_test_client() -> TestClient:
    settings = Settings(
        _env_file=None,
        app_environment="testing",
        app_debug=False,
    )

    return TestClient(create_app(settings))


def test_generated_correlation_id_is_returned_in_response() -> None:
    client = create_test_client()

    response = client.get("/api/v1/health")

    assert response.status_code == 200

    correlation_id = response.headers[CORRELATION_ID_HEADER]

    assert str(UUID(correlation_id)) == correlation_id


def test_valid_caller_correlation_id_is_preserved() -> None:
    client = create_test_client()
    supplied_correlation_id = str(uuid4())

    response = client.get(
        "/api/v1/health",
        headers={CORRELATION_ID_HEADER: supplied_correlation_id},
    )

    assert response.headers[CORRELATION_ID_HEADER] == supplied_correlation_id


def test_invalid_caller_correlation_id_is_replaced() -> None:
    client = create_test_client()

    response = client.get(
        "/api/v1/health",
        headers={CORRELATION_ID_HEADER: "not-a-valid-uuid"},
    )

    returned_correlation_id = response.headers[CORRELATION_ID_HEADER]

    assert returned_correlation_id != "not-a-valid-uuid"
    assert str(UUID(returned_correlation_id)) == returned_correlation_id


def test_correlation_id_is_available_inside_request_context() -> None:
    settings = Settings(
        _env_file=None,
        app_environment="testing",
        app_debug=False,
    )
    app = create_app(settings)

    @app.get("/test/correlation-context")
    async def correlation_context(request: Request) -> dict[str, str | None]:
        return {
            "request_state": request.state.correlation_id,
            "context_value": get_correlation_id(),
        }

    client = TestClient(app)
    supplied_correlation_id = str(uuid4())

    response = client.get(
        "/test/correlation-context",
        headers={CORRELATION_ID_HEADER: supplied_correlation_id},
    )

    payload = response.json()

    assert payload["request_state"] == supplied_correlation_id
    assert payload["context_value"] == supplied_correlation_id