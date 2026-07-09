from intentforge_api.auth.passwords import PasswordSecurityService


def test_password_hashing_and_verification_round_trip() -> None:
    service = PasswordSecurityService(iterations=1_000, salt_size=8)

    password_hash = service.hash_password("correct horse battery staple")

    assert password_hash != "correct horse battery staple"
    assert service.verify_password("correct horse battery staple", password_hash) is True
    assert service.verify_password("incorrect", password_hash) is False


def test_password_hashes_use_unique_salts() -> None:
    service = PasswordSecurityService(iterations=1_000, salt_size=8)

    first_hash = service.hash_password("same password")
    second_hash = service.hash_password("same password")

    assert first_hash != second_hash


def test_malformed_password_hash_fails_safely() -> None:
    service = PasswordSecurityService(iterations=1_000, salt_size=8)

    assert service.verify_password("password", "malformed") is False
    assert service.needs_rehash("malformed") is True


def test_rehash_detection_responds_to_iteration_changes() -> None:
    old_service = PasswordSecurityService(iterations=1_000, salt_size=8)
    new_service = PasswordSecurityService(iterations=2_000, salt_size=8)

    password_hash = old_service.hash_password("rehash me")

    assert new_service.needs_rehash(password_hash) is True
    assert old_service.needs_rehash(password_hash) is False
