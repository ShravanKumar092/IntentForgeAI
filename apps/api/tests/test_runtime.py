from intentforge_api.core.config import Environment, Settings
from intentforge_api.core.runtime import RuntimeIdentity


def test_runtime_identity_is_created_from_settings() -> None:
    settings = Settings(
        _env_file=None,
        app_name="IntentForge Test",
        app_version="9.9.9",
        app_environment="testing",
        app_debug=False,
    )

    runtime = RuntimeIdentity.from_settings(settings)

    assert runtime.application == "IntentForge Test"
    assert runtime.version == "9.9.9"
    assert runtime.environment is Environment.TESTING
    assert runtime.debug is False