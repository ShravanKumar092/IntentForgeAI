from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from intentforge_api.core.correlation import (
    CORRELATION_ID_HEADER,
    reset_correlation_id,
    resolve_correlation_id,
    set_correlation_id,
)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        correlation_id = resolve_correlation_id(
            request.headers.get(CORRELATION_ID_HEADER)
        )

        token = set_correlation_id(correlation_id)
        request.state.correlation_id = correlation_id

        try:
            response = await call_next(request)
            response.headers[CORRELATION_ID_HEADER] = correlation_id
            return response
        finally:
            reset_correlation_id(token)