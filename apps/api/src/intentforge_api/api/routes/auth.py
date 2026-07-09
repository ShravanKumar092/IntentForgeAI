from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from intentforge_api.auth.dependencies import (
    get_authenticated_principal,
    get_password_service,
    get_token_service,
    get_user_repository,
    normalize_login_email,
)
from intentforge_api.auth.passwords import PasswordSecurityService
from intentforge_api.auth.repository import DuplicateIdentityError, SqlAlchemyUserRepository
from intentforge_api.auth.schemas import (
    AccessTokenResponse,
    AuthenticationPrincipal,
    LoginRequest,
    PublicUser,
    RegisterRequest,
)
from intentforge_api.auth.tokens import AccessTokenService


logger = logging.getLogger("intentforge.security")
router = APIRouter(tags=["auth"])


def _public_user_from_model(user) -> PublicUser:
    return PublicUser.model_validate(user)


@router.post("/auth/register", response_model=PublicUser, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    repository: SqlAlchemyUserRepository = Depends(get_user_repository),
    password_service: PasswordSecurityService = Depends(get_password_service),
) -> PublicUser:
    normalized_email = normalize_login_email(payload.email)
    existing_user = await repository.find_by_email(normalized_email)
    if existing_user is not None:
        logger.info(
            "Registration rejected",
            extra={
                "event": "registration_rejected",
                "reason": "duplicate_identity",
            },
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Identity already exists",
        )

    password_hash = password_service.hash_password(payload.password.get_secret_value())

    try:
        user = await repository.create(
            email=normalized_email,
            password_hash=password_hash,
        )
        await repository.session.commit()
    except DuplicateIdentityError:
        logger.info(
            "Registration rejected",
            extra={
                "event": "registration_rejected",
                "reason": "duplicate_identity",
            },
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Identity already exists",
        )

    logger.info(
        "Registration succeeded",
        extra={
            "event": "registration_succeeded",
            "identity_id": str(user.id),
        },
    )
    return _public_user_from_model(user)


@router.post("/auth/login", response_model=AccessTokenResponse)
async def login(
    payload: LoginRequest,
    repository: SqlAlchemyUserRepository = Depends(get_user_repository),
    password_service: PasswordSecurityService = Depends(get_password_service),
    token_service: AccessTokenService = Depends(get_token_service),
) -> AccessTokenResponse:
    normalized_email = normalize_login_email(payload.email)
    user = await repository.find_by_email(normalized_email)

    password_value = payload.password.get_secret_value()
    if user is None or not password_service.verify_password(password_value, user.password_hash):
        logger.info(
            "Login failed",
            extra={
                "event": "login_failed",
                "reason": "invalid_credentials",
            },
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        logger.info(
            "Login failed",
            extra={
                "event": "login_failed",
                "reason": "inactive_identity",
                "identity_id": str(user.id),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive identity",
        )

    if password_service.needs_rehash(user.password_hash):
        refreshed_hash = password_service.hash_password(password_value)
        user.password_hash = refreshed_hash
        await repository.session.commit()

    token_bundle = token_service.create_access_token(user.id)

    logger.info(
        "Login succeeded",
        extra={
            "event": "login_succeeded",
            "identity_id": str(user.id),
        },
    )
    return AccessTokenResponse(
        access_token=token_bundle.token,
        token_type="bearer",
        expires_at=token_bundle.expires_at,
        user=_public_user_from_model(user),
    )


@router.get("/auth/me", response_model=PublicUser)
async def me(principal: AuthenticationPrincipal = Depends(get_authenticated_principal)) -> PublicUser:
    return _public_user_from_model(principal.user)
