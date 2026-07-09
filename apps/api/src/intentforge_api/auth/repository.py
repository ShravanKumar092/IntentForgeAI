from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from intentforge_api.auth.models import User


class DuplicateIdentityError(RuntimeError):
    pass


class SqlAlchemyUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_by_id(self, user_id: UUID) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def find_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, *, email: str, password_hash: str, is_active: bool = True) -> User:
        user = User(
            email=email,
            password_hash=password_hash,
            is_active=is_active,
        )
        self.session.add(user)

        try:
            await self.session.flush()
        except IntegrityError as exc:
            raise DuplicateIdentityError("identity already exists") from exc

        await self.session.refresh(user)
        return user
