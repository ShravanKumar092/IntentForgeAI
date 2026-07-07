import json
import logging
from datetime import UTC, datetime
from typing import Any

from intentforge_api.core.correlation import get_correlation_id


_STANDARD_LOG_RECORD_FIELDS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "taskName",
    "thread",
    "threadName",
}

_INTENTFORGE_HANDLER_MARKER = "_intentforge_json_handler"


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "severity": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": get_correlation_id(),
        }

        for key, value in record.__dict__.items():
            if key not in _STANDARD_LOG_RECORD_FIELDS and not key.startswith("_"):
                payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


def configure_logging(log_level: str) -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level.upper())

    for existing_handler in list(root_logger.handlers):
        if getattr(existing_handler, _INTENTFORGE_HANDLER_MARKER, False):
            root_logger.removeHandler(existing_handler)

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    setattr(handler, _INTENTFORGE_HANDLER_MARKER, True)

    root_logger.addHandler(handler)
