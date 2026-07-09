from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest

from intentforge_api.auth.tokens import AccessTokenService, InvalidTokenError
from intentforge_api.core.config import Settings


def build_token_service(secret: str = "super-secret-super-secret-super-secret") -> AccessTokenService:
    settings = Settings(
        _env_file=None,
        app_environment="testing",
        app_debug=False,
        token_signing_secret=secret,
        token_issuer="intentforge-api",
        token_audience="intentforge-api",
    )
    return AccessTokenService(settings)


def test_access_token_creation_and_validation_round_trip() -> None:
    service = build_token_service()
    subject = uuid4()

    token_bundle = service.create_access_token(subject)
    claims = service.decode_access_token(token_bundle.token)

    assert claims.subject == subject
    assert claims.token_type == "access"
    assert claims.issuer == "intentforge-api"
    assert claims.audience == "intentforge-api"
    assert claims.expires_at > claims.issued_at


def test_access_token_rejects_invalid_signature() -> None:
    service = build_token_service()
    other_service = build_token_service("another-super-secret-another-super-secret")

    token_bundle = other_service.create_access_token(uuid4())

    with pytest.raises(InvalidTokenError):
        service.decode_access_token(token_bundle.token)


def test_access_token_rejects_malformed_token() -> None:
    service = build_token_service()

    with pytest.raises(InvalidTokenError):
        service.decode_access_token("not-a-token")


def test_access_token_rejects_wrong_token_type() -> None:
    service = build_token_service()
    now = datetime.now(UTC)
    token = jwt.encode(
        {
            "sub": str(uuid4()),
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=5)).timestamp()),
            "iss": "intentforge-api",
            "aud": "intentforge-api",
            "token_type": "refresh",
        },
        "super-secret-super-secret-super-secret",
        algorithm="HS256",
    )

    with pytest.raises(InvalidTokenError):
        service.decode_access_token(token)


def test_access_token_rejects_expired_token() -> None:
    service = build_token_service()
    now = datetime.now(UTC)
    token = jwt.encode(
        {
            "sub": str(uuid4()),
            "iat": int((now - timedelta(minutes=10)).timestamp()),
            "exp": int((now - timedelta(minutes=5)).timestamp()),
            "iss": "intentforge-api",
            "aud": "intentforge-api",
            "token_type": "access",
        },
        "super-secret-super-secret-super-secret",
        algorithm="HS256",
    )

    with pytest.raises(InvalidTokenError):
        service.decode_access_token(token)


def test_access_token_rejects_missing_subject() -> None:
    service = build_token_service()
    now = datetime.now(UTC)
    token = jwt.encode(
        {
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=5)).timestamp()),
            "iss": "intentforge-api",
            "aud": "intentforge-api",
            "token_type": "access",
        },
        "super-secret-super-secret-super-secret",
        algorithm="HS256",
    )

    with pytest.raises(InvalidTokenError):
        service.decode_access_token(token)


def test_access_token_rejects_wrong_issuer_and_audience() -> None:
    service = build_token_service()
    now = datetime.now(UTC)

    wrong_issuer_token = jwt.encode(
        {
            "sub": str(uuid4()),
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=5)).timestamp()),
            "iss": "wrong-issuer",
            "aud": "intentforge-api",
            "token_type": "access",
        },
        "super-secret-super-secret-super-secret",
        algorithm="HS256",
    )

    wrong_audience_token = jwt.encode(
        {
            "sub": str(uuid4()),
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=5)).timestamp()),
            "iss": "intentforge-api",
            "aud": "wrong-audience",
            "token_type": "access",
        },
        "super-secret-super-secret-super-secret",
        algorithm="HS256",
    )

    with pytest.raises(InvalidTokenError):
        service.decode_access_token(wrong_issuer_token)

    with pytest.raises(InvalidTokenError):
        service.decode_access_token(wrong_audience_token)
