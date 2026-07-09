from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from intentforge_api.cache.connection import RedisConnectivityError, probe_redis_connection
from intentforge_api.db.connection import DatabaseConnectivityError, probe_database_connection


router = APIRouter(tags=["readiness"])


class ReadinessResponse(BaseModel):
    status: Literal["ready", "unavailable"]
    database: Literal["available", "unavailable"]
    redis: Literal["available", "unavailable"]
    timestamp: datetime


@router.get("/readiness", response_model=ReadinessResponse)
async def readiness_check(request: Request) -> ReadinessResponse | JSONResponse:
    database_engine = request.app.state.database_engine
    redis_client = request.app.state.redis_client

    database_available = True
    redis_available = True

    try:
        await probe_database_connection(database_engine)
    except DatabaseConnectivityError:
        database_available = False

    try:
        await probe_redis_connection(redis_client)
    except RedisConnectivityError:
        redis_available = False

    if database_available and redis_available:
        return ReadinessResponse(
            status="ready",
            database="available",
            redis="available",
            timestamp=datetime.now(UTC),
        )

    return JSONResponse(
        status_code=503,
        content={
            "status": "unavailable",
            "database": "available" if database_available else "unavailable",
            "redis": "available" if redis_available else "unavailable",
            "timestamp": datetime.now(UTC).isoformat(),
        },
    )
