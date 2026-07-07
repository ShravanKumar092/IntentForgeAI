from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, Request
from pydantic import BaseModel

from intentforge_api.core.runtime import RuntimeIdentity


router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: Literal["healthy"]
    service: str
    version: str
    environment: str
    debug: bool
    timestamp: datetime


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request) -> HealthResponse:
    runtime: RuntimeIdentity = request.app.state.runtime_identity

    return HealthResponse(
        status="healthy",
        service=runtime.application,
        version=runtime.version,
        environment=runtime.environment.value,
        debug=runtime.debug,
        timestamp=datetime.now(UTC),
    )