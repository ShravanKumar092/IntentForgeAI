from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine


class DatabaseConnectivityError(RuntimeError):
    pass


async def probe_database_connection(engine: AsyncEngine) -> None:
    try:
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT 1"))
            if result.scalar_one() != 1:
                raise DatabaseConnectivityError("database connectivity check returned an unexpected result")
    except (OSError, SQLAlchemyError) as exc:
        raise DatabaseConnectivityError("database connectivity check failed") from exc
