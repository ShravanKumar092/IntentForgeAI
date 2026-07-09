import pytest
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncEngine

from intentforge_api.core.config import Settings
from intentforge_api.db.connection import DatabaseConnectivityError, probe_database_connection
from intentforge_api.db.engine import create_database_engine
from intentforge_api.db.session import create_session_factory


def test_database_configuration_defaults_and_url_secrecy() -> None:
    settings = Settings(_env_file=None)

    assert settings.postgres_host == "127.0.0.1"
    assert settings.postgres_port == 5432
    assert settings.postgres_database == "intentforge_db"
    assert settings.postgres_user == "intentforge"
    assert settings.postgres_password.get_secret_value() == "change_me"

    representation = repr(settings)
    url_string = str(settings.database_url)

    assert "change_me" not in representation
    assert "change_me" not in url_string
    assert settings.database_url.drivername == "postgresql+asyncpg"


def test_database_port_validation_is_enforced() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, postgres_port=0)


def test_database_engine_is_derived_from_settings() -> None:
    settings = Settings(
        _env_file=None,
        postgres_host="db.internal",
        postgres_port=5544,
        postgres_database="intentforge_test",
        postgres_user="intentforge_test_user",
        postgres_password="super-secret",
    )

    engine = create_database_engine(settings)

    assert isinstance(engine, AsyncEngine)
    assert engine.url.drivername == "postgresql+asyncpg"
    assert engine.url.host == "db.internal"
    assert engine.url.port == 5544
    assert engine.url.database == "intentforge_test"
    assert engine.url.username == "intentforge_test_user"
    assert engine.url.password == "super-secret"


def test_session_factory_is_deterministic_and_engine_bound() -> None:
    settings = Settings(_env_file=None)
    engine = create_database_engine(settings)

    session_factory = create_session_factory(engine)

    assert session_factory.kw["bind"] is engine
    assert session_factory.kw["expire_on_commit"] is False
    assert session_factory.kw["autoflush"] is False


class _SuccessfulResult:
    def scalar_one(self) -> int:
        return 1


class _SuccessfulConnection:
    async def execute(self, statement) -> _SuccessfulResult:
        return _SuccessfulResult()


class _SuccessfulConnectionContext:
    async def __aenter__(self) -> _SuccessfulConnection:
        return _SuccessfulConnection()

    async def __aexit__(self, exc_type, exc, traceback) -> None:
        return None


class _SuccessfulEngine:
    def connect(self) -> _SuccessfulConnectionContext:
        return _SuccessfulConnectionContext()


class _FailingConnection:
    async def execute(self, statement):
        raise ConnectionRefusedError("boom")


class _FailingConnectionContext:
    async def __aenter__(self) -> _FailingConnection:
        return _FailingConnection()

    async def __aexit__(self, exc_type, exc, traceback) -> None:
        return None


class _FailingEngine:
    def connect(self) -> _FailingConnectionContext:
        return _FailingConnectionContext()


@pytest.mark.asyncio
async def test_database_probe_succeeds_with_select_one() -> None:
    await probe_database_connection(_SuccessfulEngine())


@pytest.mark.asyncio
async def test_database_probe_failure_is_explicit() -> None:
    with pytest.raises(DatabaseConnectivityError):
        await probe_database_connection(_FailingEngine())
