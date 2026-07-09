from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, SecretStr

from intentforge_api.auth.models import User


class RegisterRequest(BaseModel):
    email: str
    password: SecretStr


class LoginRequest(BaseModel):
    email: str
    password: SecretStr


class PublicUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"]
    expires_at: datetime
    user: PublicUser


@dataclass(slots=True)
class AuthenticationPrincipal:
    user: User
    token_subject: UUID
    token_type: str
    token_expires_at: datetime
