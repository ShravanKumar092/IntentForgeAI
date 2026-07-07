from enum import StrEnum
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    )

    app_name: str = "IntentForge AI"
    app_version: str = "0.1.0"
    app_environment: Environment = Environment.DEVELOPMENT
    app_debug: bool = True

    api_host: str = "127.0.0.1"
    api_port: int = Field(default=8010, ge=1, le=65535)

    log_level: str = "INFO"

    @property
    def is_production(self) -> bool:
        return self.app_environment is Environment.PRODUCTION


@lru_cache
def get_settings() -> Settings:
    return Settings()