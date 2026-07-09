import re

from intentforge_api.core.config import Settings

_SEGMENT_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_REDIS_KEY_PREFIX = "intentforge"


def _validate_segment(segment_name: str, value: str) -> str:
    if not value:
        raise ValueError(f"{segment_name} cannot be empty")
    if not _SEGMENT_PATTERN.fullmatch(value):
        raise ValueError(f"{segment_name} contains invalid characters")
    return value


def build_redis_key(settings: Settings, capability: str, identifier: str) -> str:
    environment = _validate_segment("environment", settings.app_environment.value)
    validated_capability = _validate_segment("capability", capability)
    validated_identifier = _validate_segment("identifier", identifier)

    return f"{_REDIS_KEY_PREFIX}:{environment}:{validated_capability}:{validated_identifier}"
