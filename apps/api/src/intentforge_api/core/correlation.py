from contextvars import ContextVar, Token
from uuid import UUID, uuid4


CORRELATION_ID_HEADER = "X-Correlation-ID"

_correlation_id_context: ContextVar[str | None] = ContextVar(
    "correlation_id",
    default=None,
)


def generate_correlation_id() -> str:
    return str(uuid4())


def is_valid_correlation_id(value: str) -> bool:
    try:
        UUID(value)
    except (ValueError, AttributeError):
        return False

    return True


def resolve_correlation_id(candidate: str | None) -> str:
    if candidate is not None and is_valid_correlation_id(candidate):
        return candidate

    return generate_correlation_id()


def set_correlation_id(correlation_id: str) -> Token[str | None]:
    return _correlation_id_context.set(correlation_id)


def get_correlation_id() -> str | None:
    return _correlation_id_context.get()


def reset_correlation_id(token: Token[str | None]) -> None:
    _correlation_id_context.reset(token)