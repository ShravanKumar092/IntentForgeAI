from __future__ import annotations

import base64
import binascii
import hashlib
import os
import secrets
from dataclasses import dataclass


@dataclass(slots=True)
class PasswordSecurityService:
    algorithm_name: str = "pbkdf2_sha256"
    iterations: int = 600_000
    salt_size: int = 16

    def hash_password(self, password: str) -> str:
        salt = os.urandom(self.salt_size)
        derived_key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            self.iterations,
        )
        return "$".join(
            (
                self.algorithm_name,
                str(self.iterations),
                base64.urlsafe_b64encode(salt).decode("ascii"),
                base64.urlsafe_b64encode(derived_key).decode("ascii"),
            )
        )

    def verify_password(self, password: str, encoded_hash: str) -> bool:
        try:
            algorithm_name, iterations_text, salt_text, hash_text = encoded_hash.split("$", 3)
            iterations = int(iterations_text)
            if algorithm_name != self.algorithm_name:
                return False

            salt = base64.urlsafe_b64decode(salt_text.encode("ascii"))
            expected_hash = base64.urlsafe_b64decode(hash_text.encode("ascii"))
        except (ValueError, UnicodeError, binascii.Error):
            return False

        derived_key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations,
        )
        return secrets.compare_digest(derived_key, expected_hash)

    def needs_rehash(self, encoded_hash: str) -> bool:
        try:
            algorithm_name, iterations_text, *_ = encoded_hash.split("$", 3)
            iterations = int(iterations_text)
        except ValueError:
            return True

        return algorithm_name != self.algorithm_name or iterations != self.iterations
