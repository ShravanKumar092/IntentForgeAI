from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from intentforge_api.db.connection import DatabaseConnectivityError, probe_database_connection


router = APIRouter(tags=["readiness"])


class ReadinessResponse(BaseModel):
    status: Literal["ready"]
    database: Literal["available"]
    timestamp: datetime


@router.get("/readiness", response_model=ReadinessResponse)
async def readiness_check(request: Request) -> ReadinessResponse | JSONResponse:
    database_engine = request.app.state.database_engine

    try:
        await probe_database_connection(database_engine)
    except DatabaseConnectivityError:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unavailable",
                "database": "unavailable",
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

    return ReadinessResponse(
        status="ready",
        database="available",
        timestamp=datetime.now(UTC),
    )
