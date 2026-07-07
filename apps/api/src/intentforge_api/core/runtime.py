from dataclasses import dataclass

from intentforge_api.core.config import Environment, Settings


@dataclass(frozen=True, slots=True)
class RuntimeIdentity:
    application: str
    version: str
    environment: Environment
    debug: bool

    @classmethod
    def from_settings(cls, settings: Settings) -> "RuntimeIdentity":
        return cls(
            application=settings.app_name,
            version=settings.app_version,
            environment=settings.app_environment,
            debug=settings.app_debug,
        )