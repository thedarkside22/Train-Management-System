"""Field-level encryption: cipher behaviour and key loading."""

import pytest

SECRET = "unit-test-secret-0123456789-abcdefghij"
OTHER_SECRET = "another-test-secret-9876543210-zyxwvut"


def test_encrypt_hides_the_value_and_decrypt_restores_it():
    from encryption import FieldCipher

    cipher = FieldCipher(SECRET)
    token = cipher.encrypt("1100000001")

    assert "1100000001" not in token
    assert cipher.decrypt(token) == "1100000001"


def test_same_value_encrypts_differently_each_time():
    from encryption import FieldCipher

    cipher = FieldCipher(SECRET)

    assert cipher.encrypt("0501111111") != cipher.encrypt("0501111111")


def test_decrypt_with_a_different_key_fails():
    from encryption import FieldCipher, WrongKeyError

    token = FieldCipher(SECRET).encrypt("1100000001")

    with pytest.raises(WrongKeyError):
        FieldCipher(OTHER_SECRET).decrypt(token)


def test_blind_index_is_stable_for_the_same_value():
    from encryption import FieldCipher

    cipher = FieldCipher(SECRET)

    assert cipher.blind_index("national_id", "1100000001") == cipher.blind_index("national_id", "1100000001")


def test_blind_index_does_not_reveal_the_value():
    from encryption import FieldCipher

    digest = FieldCipher(SECRET).blind_index("national_id", "1100000001")

    assert "1100000001" not in digest
    assert len(digest) == 64


def test_blind_index_differs_per_value_field_and_key():
    from encryption import FieldCipher

    cipher = FieldCipher(SECRET)
    digest = cipher.blind_index("national_id", "1100000001")

    assert digest != cipher.blind_index("national_id", "1100000002")
    assert digest != cipher.blind_index("phone", "1100000001")
    assert digest != FieldCipher(OTHER_SECRET).blind_index("national_id", "1100000001")


def test_blind_index_ignores_case_and_surrounding_spaces():
    from encryption import FieldCipher

    cipher = FieldCipher(SECRET)

    assert cipher.blind_index("email", "  P1@X.com ") == cipher.blind_index("email", "p1@x.com")


def test_short_secret_is_rejected():
    from encryption import FieldCipher

    with pytest.raises(ValueError, match="at least 32"):
        FieldCipher("too-short")


def test_secret_comes_from_the_environment(monkeypatch):
    from encryption import load_secret

    monkeypatch.setenv("DATA_ENCRYPTION_KEY", SECRET)

    assert load_secret() == SECRET


def test_missing_secret_stops_a_postgres_deployment(monkeypatch):
    from encryption import load_secret

    monkeypatch.delenv("DATA_ENCRYPTION_KEY", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql://app:pw@db.example.com/trains")

    with pytest.raises(RuntimeError, match="DATA_ENCRYPTION_KEY"):
        load_secret()


def test_local_sqlite_generates_a_key_file_and_reuses_it(monkeypatch, tmp_path):
    import encryption

    key_file = tmp_path / ".data_encryption_key"
    monkeypatch.delenv("DATA_ENCRYPTION_KEY", raising=False)
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./local.db")
    monkeypatch.setattr(encryption, "LOCAL_KEY_FILE", key_file)

    first = encryption.load_secret()

    assert key_file.read_text().strip() == first
    assert len(first) >= 32
    assert encryption.load_secret() == first
