from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt

from intentforge_api.core.config import Settings


class InvalidTokenError(RuntimeError):
    pass


@dataclass(slots=True)
class AccessTokenClaims:
    subject: UUID
    issued_at: datetime
    expires_at: datetime
    issuer: str
    audience: str
    token_type: str


@dataclass(slots=True)
class AccessTokenBundle:
    token: str
    expires_at: datetime


class AccessTokenService:
    def __init__(self, settings: Settings) -> None:
        self._secret = settings.token_signing_secret.get_secret_value()
        self._algorithm = settings.token_signing_algorithm
        self._issuer = settings.token_issuer
        self._audience = settings.token_audience
        self._access_token_minutes = settings.access_token_expire_minutes

    def create_access_token(self, subject: UUID) -> AccessTokenBundle:
        issued_at = datetime.now(UTC)
        expires_at = issued_at + timedelta(minutes=self._access_token_minutes)

        payload = {
            "sub": str(subject),
            "iat": int(issued_at.timestamp()),
            "exp": int(expires_at.timestamp()),
            "iss": self._issuer,
            "aud": self._audience,
            "token_type": "access",
        }

        token = jwt.encode(payload, self._secret, algorithm=self._algorithm)
        return AccessTokenBundle(token=token, expires_at=expires_at)

    def decode_access_token(self, token: str) -> AccessTokenClaims:
        try:
            payload = jwt.decode(
                token,
                self._secret,
                algorithms=[self._algorithm],
                issuer=self._issuer,
                audience=self._audience,
                options={
                    "require": ["sub", "iat", "exp", "iss", "aud", "token_type"],
                },
            )
        except jwt.PyJWTError as exc:
            raise InvalidTokenError("access token validation failed") from exc

        if payload.get("token_type") != "access":
            raise InvalidTokenError("unexpected token type")

        try:
            subject = UUID(str(payload["sub"]))
            issued_at = datetime.fromtimestamp(int(payload["iat"]), UTC)
            expires_at = datetime.fromtimestamp(int(payload["exp"]), UTC)
        except (KeyError, TypeError, ValueError) as exc:
            raise InvalidTokenError("access token payload is invalid") from exc

        return AccessTokenClaims(
            subject=subject,
            issued_at=issued_at,
            expires_at=expires_at,
            issuer=str(payload["iss"]),
            audience=str(payload["aud"]),
            token_type=str(payload["token_type"]),
        )
