"""
encryption.py - Field-level encryption for passenger personal data.

Extra layer of protection: sensitive columns are encrypted before they reach
the database, so a stolen database file, backup or SQL dump does not expose
national IDs, phone numbers or emails.

Two tools are provided:

* encrypt / decrypt: Fernet (AES-CBC plus an HMAC-SHA256 integrity check).
  A fresh random IV is used every time, so the same value never produces the
  same ciphertext twice.

* blind_index: a keyed HMAC-SHA256 of the value. Because ciphertexts are
  random they cannot be searched, so every encrypted column has a companion
  "*_hash" column that holds this digest. It is used for exact lookups and
  duplicate checks. It must be keyed: there are only about two billion valid
  national IDs, so a plain SHA-256 could be reversed by trying them all.

Both keys are derived (HKDF) from a single secret, DATA_ENCRYPTION_KEY.
Losing that secret means losing the encrypted data, so back it up.
"""

import base64
import hashlib
import hmac
from functools import lru_cache
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from sqlalchemy.types import String, TypeDecorator

import app_secrets
from app_secrets import MIN_SECRET_LENGTH

SECRET_ENV_VAR = "DATA_ENCRYPTION_KEY"

# Room for the ciphertext of a value up to 127 bytes long (emails are capped at 100).
CIPHERTEXT_LENGTH = 255

# Only used for local SQLite development. Listed in .gitignore.
LOCAL_KEY_FILE = Path(__file__).resolve().parent / ".data_encryption_key"


class WrongKeyError(RuntimeError):
    """The stored value was encrypted with a different key, or was tampered with."""


def _derive_key(secret: str, purpose: bytes) -> bytes:
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=purpose).derive(secret.encode())


class FieldCipher:
    """Encrypts, decrypts and indexes single field values with keys derived from one secret."""

    def __init__(self, secret: str):
        if len(secret) < MIN_SECRET_LENGTH:
            raise ValueError(f"{SECRET_ENV_VAR} must be at least {MIN_SECRET_LENGTH} characters long")
        self._fernet = Fernet(base64.urlsafe_b64encode(_derive_key(secret, b"field-encryption")))
        self._index_key = _derive_key(secret, b"blind-index")

    def encrypt(self, value: str) -> str:
        return self._fernet.encrypt(value.encode()).decode()

    def decrypt(self, token: str) -> str:
        try:
            return self._fernet.decrypt(token.encode()).decode()
        except InvalidToken as exc:
            raise WrongKeyError(
                f"Could not decrypt a stored value. {SECRET_ENV_VAR} does not match "
                "the key that was used to encrypt the data."
            ) from exc

    def blind_index(self, field: str, value: str) -> str:
        """Keyed digest used for exact-match lookups. The field name keeps columns apart."""
        message = f"{field}:{value.strip().lower()}".encode()
        return hmac.new(self._index_key, message, hashlib.sha256).hexdigest()


def load_secret() -> str:
    """The secret that every passenger-data key is derived from (see app_secrets.py)."""
    return app_secrets.load_secret(SECRET_ENV_VAR, LOCAL_KEY_FILE)


@lru_cache(maxsize=1)
def get_cipher() -> FieldCipher:
    return FieldCipher(load_secret())


def encrypt(value: str) -> str:
    return get_cipher().encrypt(value)


def decrypt(token: str) -> str:
    return get_cipher().decrypt(token)


def blind_index(field: str, value: str) -> str:
    return get_cipher().blind_index(field, value)


class EncryptedString(TypeDecorator):
    """Column type that stores ciphertext and hands plaintext to the application."""

    impl = String(CIPHERTEXT_LENGTH)
    cache_ok = True

    class comparator_factory(TypeDecorator.Comparator):
        """Ciphertext is random, so comparing it would silently match nothing. Fail loudly instead."""

        def operate(self, op, *other, **kwargs):
            raise TypeError(
                "Encrypted columns cannot be filtered or sorted. "
                "Compare the matching *_hash column with blind_index() instead."
            )

        reverse_operate = operate

    def process_bind_param(self, value, dialect):
        return None if value is None else encrypt(value)

    def process_result_value(self, value, dialect):
        return None if value is None else decrypt(value)
