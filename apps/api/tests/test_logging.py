import json
import logging
from io import StringIO
from uuid import uuid4

from fastapi.testclient import TestClient

from intentforge_api.core.config import Settings
from intentforge_api.core.correlation import (
    CORRELATION_ID_HEADER,
    reset_correlation_id,
    set_correlation_id,
)
from intentforge_api.core.logging import JsonFormatter
from intentforge_api.main import create_app


def test_json_formatter_emits_required_fields() -> None:
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())

    logger = logging.getLogger("intentforge.test.formatter")
    logger.handlers = [handler]
    logger.propagate = False
    logger.setLevel(logging.INFO)

    correlation_id = str(uuid4())
    token = set_correlation_id(correlation_id)

    try:
        logger.info(
            "Verification event",
            extra={
                "event": "verification_event",
                "result": "pass",
            },
        )
    finally:
        reset_correlation_id(token)

    payload = json.loads(stream.getvalue())

    assert payload["severity"] == "INFO"
    assert payload["logger"] == "intentforge.test.formatter"
    assert payload["message"] == "Verification event"
    assert payload["correlation_id"] == correlation_id
    assert payload["event"] == "verification_event"
    assert payload["result"] == "pass"
    assert "timestamp" in payload


def test_request_logs_share_response_correlation_id(caplog) -> None:
    settings = Settings(
        _env_file=None,
        app_environment="testing",
        app_debug=False,
        log_level="INFO",
    )
    client = TestClient(create_app(settings))
    correlation_id = str(uuid4())

    with caplog.at_level(logging.INFO, logger="intentforge.request"):
        response = client.get(
            "/api/v1/health",
            headers={CORRELATION_ID_HEADER: correlation_id},
        )

    assert response.status_code == 200
    assert response.headers[CORRELATION_ID_HEADER] == correlation_id

    request_records = [
        record
        for record in caplog.records
        if record.name == "intentforge.request"
    ]

    assert len(request_records) == 2
    assert request_records[0].event == "http_request_started"
    assert request_records[1].event == "http_request_completed"

    assert request_records[0].method == "GET"
    assert request_records[0].path == "/api/v1/health"

    assert request_records[1].method == "GET"
    assert request_records[1].path == "/api/v1/health"
    assert request_records[1].status_code == 200
    assert request_records[1].duration_ms >= 0
