from contextlib import asynccontextmanager

from fastapi import FastAPI

from intentforge_api.api.routes.health import router as health_router
from intentforge_api.api.routes.readiness import router as readiness_router
from intentforge_api.core.config import Settings, get_settings
from intentforge_api.core.logging import configure_logging
from intentforge_api.core.runtime import RuntimeIdentity
from intentforge_api.cache.client import create_redis_client
from intentforge_api.db.engine import create_database_engine
from intentforge_api.db.session import create_session_factory
from intentforge_api.middleware.correlation import CorrelationIdMiddleware
from intentforge_api.middleware.request_logging import RequestLoggingMiddleware


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    runtime_identity = RuntimeIdentity.from_settings(resolved_settings)
    database_engine = create_database_engine(resolved_settings)
    database_session_factory = create_session_factory(database_engine)
    redis_client = create_redis_client(resolved_settings)

    configure_logging(resolved_settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        await redis_client.aclose()
        await database_engine.dispose()

    app = FastAPI(
        title=runtime_identity.application,
        description="Evidence-governed project intelligence and engineering platform.",
        version=runtime_identity.version,
        debug=runtime_identity.debug,
        lifespan=lifespan,
    )

    app.state.settings = resolved_settings
    app.state.runtime_identity = runtime_identity
    app.state.database_engine = database_engine
    app.state.database_session_factory = database_session_factory
    app.state.redis_client = redis_client

    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(CorrelationIdMiddleware)

    app.include_router(health_router, prefix="/api/v1")
    app.include_router(readiness_router, prefix="/api/v1")

    return app


app = create_app()
