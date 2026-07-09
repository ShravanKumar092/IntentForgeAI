from intentforge_api.auth.models import User
from intentforge_api.auth.normalization import normalize_identity


def test_user_model_contains_only_required_identity_fields() -> None:
    assert set(User.__table__.columns.keys()) == {
        "id",
        "email",
        "password_hash",
        "is_active",
        "created_at",
        "updated_at",
    }

    assert User.__table__.c.email.unique is True
    assert User.__table__.c.password_hash.nullable is False
    assert User.__table__.c.is_active.nullable is False


def test_identity_normalization_is_deterministic() -> None:
    assert normalize_identity("  Admin@Example.COM  ") == "admin@example.com"
