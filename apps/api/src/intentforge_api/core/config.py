from enum import StrEnum
from functools import lru_cache

from pydantic import AliasChoices, Field, SecretStr
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Environment(StrEnum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        populate_by_name=True,
    )

    app_name: str = "IntentForge AI"
    app_version: str = "0.1.0"
    app_environment: Environment = Environment.DEVELOPMENT
    app_debug: bool = True

    api_host: str = "127.0.0.1"
    api_port: int = Field(default=8010, ge=1, le=65535)

    log_level: str = "INFO"

    postgres_host: str = "127.0.0.1"
    postgres_port: int = Field(default=5432, ge=1, le=65535)
    postgres_database: str = Field(
        default="intentforge_db",
        validation_alias=AliasChoices("POSTGRES_DB", "postgres_database"),
    )
    postgres_user: str = Field(
        default="intentforge",
        validation_alias=AliasChoices("POSTGRES_USER", "postgres_user"),
    )
    postgres_password: SecretStr = Field(
        default=SecretStr("change_me"),
        repr=False,
        validation_alias=AliasChoices("POSTGRES_PASSWORD", "postgres_password"),
    )

    redis_host: str = "127.0.0.1"
    redis_port: int = Field(default=6379, ge=1, le=65535)
    redis_database: int = Field(
        default=0,
        ge=0,
        validation_alias=AliasChoices("REDIS_DB", "redis_database"),
    )
    redis_timeout_seconds: float = Field(
        default=5.0,
        gt=0,
        validation_alias=AliasChoices("REDIS_TIMEOUT_SECONDS", "redis_timeout_seconds"),
    )

    token_signing_secret: SecretStr = Field(
        default=SecretStr("change_me"),
        repr=False,
        validation_alias=AliasChoices("TOKEN_SIGNING_SECRET", "SECRET_KEY", "token_signing_secret"),
    )
    token_signing_algorithm: str = Field(
        default="HS256",
        validation_alias=AliasChoices("TOKEN_SIGNING_ALGORITHM", "token_signing_algorithm"),
    )
    access_token_expire_minutes: int = Field(
        default=15,
        gt=0,
        validation_alias=AliasChoices("ACCESS_TOKEN_EXPIRE_MINUTES", "access_token_expire_minutes"),
    )
    token_issuer: str = Field(
        default="intentforge-api",
        validation_alias=AliasChoices("TOKEN_ISSUER", "token_issuer"),
    )
    token_audience: str = Field(
        default="intentforge-api",
        validation_alias=AliasChoices("TOKEN_AUDIENCE", "token_audience"),
    )

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.postgres_user,
            password=self.postgres_password.get_secret_value(),
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_database,
        )

    @property
    def redis_url(self) -> URL:
        return URL.create(
            drivername="redis",
            host=self.redis_host,
            port=self.redis_port,
            database=str(self.redis_database),
        )

    @property
    def is_production(self) -> bool:
        return self.app_environment is Environment.PRODUCTION

    @model_validator(mode="after")
    def validate_security_settings(self) -> "Settings":
        if self.app_environment is Environment.PRODUCTION:
            secret_value = self.token_signing_secret.get_secret_value()
            if secret_value in {"change_me", "development-secret"} or len(secret_value) < 32:
                raise ValueError("production token signing secret must be configured securely")

        if not self.token_signing_algorithm:
            raise ValueError("token signing algorithm must not be empty")

        if not self.token_issuer.strip():
            raise ValueError("token issuer must not be empty")

        if not self.token_audience.strip():
            raise ValueError("token audience must not be empty")

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
