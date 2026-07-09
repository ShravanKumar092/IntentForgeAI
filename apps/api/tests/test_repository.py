from uuid import uuid4

import pytest

from intentforge_api.auth.models import User
from intentforge_api.auth.repository import SqlAlchemyUserRepository


class _Result:
    def __init__(self, value):
        self._value = value

    def scalar_one_or_none(self):
        return self._value


class _Session:
    def __init__(self, result=None, fail_flush: bool = False):
        self.result = result
        self.fail_flush = fail_flush
        self.added = []
        self.executed = []
        self.flushed = False
        self.refreshed = []

    async def execute(self, statement):
        self.executed.append(statement)
        return _Result(self.result)

    def add(self, obj):
        self.added.append(obj)

    async def flush(self):
        self.flushed = True
        if self.fail_flush:
            raise RuntimeError("duplicate")

    async def refresh(self, obj):
        self.refreshed.append(obj)


@pytest.mark.asyncio
async def test_repository_find_methods_use_the_async_session() -> None:
    user = User(
        id=uuid4(),
        email="admin@example.com",
        password_hash="hash",
        is_active=True,
    )
    session = _Session(result=user)
    repository = SqlAlchemyUserRepository(session)

    found_by_email = await repository.find_by_email("admin@example.com")
    found_by_id = await repository.find_by_id(user.id)

    assert found_by_email is user
    assert found_by_id is user
    assert len(session.executed) == 2


@pytest.mark.asyncio
async def test_repository_create_adds_and_refreshes_user() -> None:
    session = _Session()
    repository = SqlAlchemyUserRepository(session)

    user = await repository.create(
        email="admin@example.com",
        password_hash="hash",
    )

    assert user.email == "admin@example.com"
    assert session.added[0] is user
    assert session.flushed is True
    assert session.refreshed[0] is user
