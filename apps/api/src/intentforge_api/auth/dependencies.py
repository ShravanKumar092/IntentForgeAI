from __future__ import annotations

import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from intentforge_api.auth.normalization import normalize_identity
from intentforge_api.auth.passwords import PasswordSecurityService
from intentforge_api.auth.repository import SqlAlchemyUserRepository
from intentforge_api.auth.schemas import AuthenticationPrincipal
from intentforge_api.auth.tokens import AccessTokenService, InvalidTokenError
from intentforge_api.core.config import Settings, get_settings
from intentforge_api.db.session import get_async_session

logger = logging.getLogger("intentforge.security")
bearer_scheme = HTTPBearer(auto_error=False)


def get_password_service() -> PasswordSecurityService:
    return PasswordSecurityService()


def get_token_service(settings: Settings = Depends(get_settings)) -> AccessTokenService:
    return AccessTokenService(settings)


def get_user_repository(session: AsyncSession = Depends(get_async_session)) -> SqlAlchemyUserRepository:
    return SqlAlchemyUserRepository(session)


def normalize_login_email(email: str) -> str:
    return normalize_identity(email)


async def get_authenticated_principal(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    repository: SqlAlchemyUserRepository = Depends(get_user_repository),
    token_service: AccessTokenService = Depends(get_token_service),
) -> AuthenticationPrincipal:
    if credentials is None or credentials.scheme.lower() != "bearer":
        logger.info(
            "Authentication rejected",
            extra={
                "event": "token_validation_failed",
                "reason": "missing_credentials",
            },
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        claims = token_service.decode_access_token(credentials.credentials)
    except InvalidTokenError:
        logger.info(
            "Authentication rejected",
            extra={
                "event": "token_validation_failed",
                "reason": "invalid_token",
            },
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await repository.find_by_id(claims.subject)
    if user is None:
        logger.info(
            "Authentication rejected",
            extra={
                "event": "token_validation_failed",
                "reason": "unknown_identity",
            },
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        logger.info(
            "Authentication rejected",
            extra={
                "event": "token_validation_failed",
                "reason": "inactive_identity",
                "identity_id": str(user.id),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive identity",
        )

    logger.info(
        "Authenticated request identity resolved",
        extra={
            "event": "authenticated_request_identity_resolved",
            "identity_id": str(user.id),
        },
    )
    return AuthenticationPrincipal(
        user=user,
        token_subject=claims.subject,
        token_type=claims.token_type,
        token_expires_at=claims.expires_at,
    )
