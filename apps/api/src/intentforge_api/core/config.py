from enum import StrEnum
from functools import lru_cache

from pydantic import AliasChoices, Field, SecretStr
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
    def is_production(self) -> bool:
        return self.app_environment is Environment.PRODUCTION


@lru_cache
def get_settings() -> Settings:
    return Settings()
