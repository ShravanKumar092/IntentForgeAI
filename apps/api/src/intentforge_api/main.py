from fastapi import FastAPI

from intentforge_api.api.routes.health import router as health_router
from intentforge_api.core.config import Settings, get_settings
from intentforge_api.core.logging import configure_logging
from intentforge_api.core.runtime import RuntimeIdentity
from intentforge_api.middleware.correlation import CorrelationIdMiddleware
from intentforge_api.middleware.request_logging import RequestLoggingMiddleware


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    runtime_identity = RuntimeIdentity.from_settings(resolved_settings)

    configure_logging(resolved_settings.log_level)

    app = FastAPI(
        title=runtime_identity.application,
        description="Evidence-governed project intelligence and engineering platform.",
        version=runtime_identity.version,
        debug=runtime_identity.debug,
    )

    app.state.settings = resolved_settings
    app.state.runtime_identity = runtime_identity

    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(CorrelationIdMiddleware)

    app.include_router(health_router, prefix="/api/v1")

    return app


app = create_app()
