from fastapi import FastAPI

from intentforge_api.api.routes.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="IntentForge AI API",
        description="Evidence-governed project intelligence and engineering platform.",
        version="0.1.0",
    )

    app.include_router(health_router, prefix="/api/v1")

    return app


app = create_app()