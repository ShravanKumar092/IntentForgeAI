from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.testclient import TestClient

from intentforge_api.auth.dependencies import (
    get_authenticated_principal,
    get_password_service,
    get_token_service,
    get_user_repository,
)
from intentforge_api.auth.models import User
from intentforge_api.auth.passwords import PasswordSecurityService
from intentforge_api.auth.schemas import AuthenticationPrincipal
from intentforge_api.auth.tokens import AccessTokenService
from intentforge_api.core.config import Settings
from intentforge_api.core.correlation import CORRELATION_ID_HEADER
from intentforge_api.main import create_app


class _NoopTransaction:
    async def __aenter__(self):
        return None

    async def __aexit__(self, exc_type, exc, traceback):
        return None


class _FakeSession:
    def begin(self):
        return _NoopTransaction()

    async def commit(self):
        return None


class _FakeUserRepository:
    def __init__(self, user: User | None = None):
        self.session = _FakeSession()
        self.user = user
        self.users_by_email: dict[str, User] = {}
        if user is not None:
            self.users_by_email[user.email] = user

    async def find_by_email(self, email: str):
        return self.users_by_email.get(email)

    async def find_by_id(self, user_id):
        if self.user is not None and self.user.id == user_id:
            return self.user
        return None

    async def create(self, *, email: str, password_hash: str, is_active: bool = True):
        now = datetime.now(UTC)
        user = User(
            id=uuid4(),
            email=email,
            password_hash=password_hash,
            is_active=is_active,
            created_at=now,
            updated_at=now,
        )
        self.user = user
        self.users_by_email[email] = user
        return user


def build_settings() -> Settings:
    return Settings(
        _env_file=None,
        app_environment="testing",
        app_debug=False,
        token_signing_secret="super-secret-super-secret-super-secret",
        token_issuer="intentforge-api",
        token_audience="intentforge-api",
    )


def build_client() -> TestClient:
    return TestClient(create_app(build_settings()))


def build_user(password: str = "correct horse battery staple") -> tuple[User, str]:
    password_service = PasswordSecurityService(iterations=1_000, salt_size=8)
    password_hash = password_service.hash_password(password)
    now = datetime.now(UTC)
    user = User(
        id=uuid4(),
        email="admin@example.com",
        password_hash=password_hash,
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    return user, password_hash


def test_register_login_and_me_flow(caplog) -> None:
    client = build_client()
    password_service = PasswordSecurityService(iterations=1_000, salt_size=8)
    token_service = AccessTokenService(build_settings())
    repository = _FakeUserRepository()
    client.app.dependency_overrides[get_user_repository] = lambda: repository
    client.app.dependency_overrides[get_password_service] = lambda: password_service
    client.app.dependency_overrides[get_token_service] = lambda: token_service

    supplied_correlation_id = str(uuid4())

    with caplog.at_level(logging.INFO, logger="intentforge.security"):
        register_response = client.post(
            "/api/v1/auth/register",
            headers={CORRELATION_ID_HEADER: supplied_correlation_id},
            json={
                "email": "  Admin@Example.COM  ",
                "password": "correct horse battery staple",
            },
        )

    assert register_response.status_code == 201
    assert register_response.headers[CORRELATION_ID_HEADER] == supplied_correlation_id
    assert register_response.json()["email"] == "admin@example.com"
    assert "password_hash" not in register_response.text
    assert "correct horse battery staple" not in caplog.text

    with caplog.at_level(logging.INFO, logger="intentforge.security"):
        login_response = client.post(
            "/api/v1/auth/login",
            headers={CORRELATION_ID_HEADER: supplied_correlation_id},
            json={
                "email": "ADMIN@example.com",
                "password": "correct horse battery staple",
            },
        )

    assert login_response.status_code == 200
    login_payload = login_response.json()
    assert login_payload["token_type"] == "bearer"
    assert login_payload["user"]["email"] == "admin@example.com"
    assert login_payload["access_token"]
    assert "correct horse battery staple" not in caplog.text

    access_token = login_payload["access_token"]

    client.app.dependency_overrides[get_authenticated_principal] = lambda: AuthenticationPrincipal(
        user=repository.user,
        token_subject=repository.user.id,
        token_type="access",
        token_expires_at=token_service.create_access_token(repository.user.id).expires_at,
    )

    me_response = client.get(
        "/api/v1/auth/me",
        headers={
            CORRELATION_ID_HEADER: supplied_correlation_id,
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert me_response.status_code == 200
    assert me_response.json()["email"] == "admin@example.com"
    client.app.dependency_overrides.clear()


def test_login_rejects_invalid_credentials() -> None:
    client = build_client()
    repository = _FakeUserRepository()
    client.app.dependency_overrides[get_user_repository] = lambda: repository

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "missing@example.com",
            "password": "wrong password",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
    client.app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_authenticated_principal_dependency_rejects_missing_and_invalid_credentials() -> None:
    settings = build_settings()
    token_service = AccessTokenService(settings)
    user, _ = build_user()

    repository = _FakeUserRepository(user=user)

    with pytest.raises(HTTPException) as missing_exc:
        await get_authenticated_principal(
            credentials=None,
            repository=repository,
            token_service=token_service,
        )

    assert missing_exc.value.status_code == 401

    with pytest.raises(HTTPException) as invalid_exc:
        await get_authenticated_principal(
            credentials=HTTPAuthorizationCredentials(scheme="Bearer", credentials="bad-token"),
            repository=repository,
            token_service=token_service,
        )

    assert invalid_exc.value.status_code == 401


@pytest.mark.asyncio
async def test_authenticated_principal_dependency_rejects_unknown_and_inactive_identities() -> None:
    settings = build_settings()
    token_service = AccessTokenService(settings)
    user, _ = build_user()
    token = token_service.create_access_token(user.id).token

    unknown_repository = _FakeUserRepository()
    with pytest.raises(HTTPException) as unknown_exc:
        await get_authenticated_principal(
            credentials=HTTPAuthorizationCredentials(scheme="Bearer", credentials=token),
            repository=unknown_repository,
            token_service=token_service,
        )

    assert unknown_exc.value.status_code == 401

    inactive_repository = _FakeUserRepository(
        user=User(
            id=user.id,
            email=user.email,
            password_hash=user.password_hash,
            is_active=False,
        )
    )
    with pytest.raises(HTTPException) as inactive_exc:
        await get_authenticated_principal(
            credentials=HTTPAuthorizationCredentials(scheme="Bearer", credentials=token),
            repository=inactive_repository,
            token_service=token_service,
        )

    assert inactive_exc.value.status_code == 403
