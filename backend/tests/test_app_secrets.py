"""Secrets come from the environment; local SQLite development gets a generated key file."""

import pytest

SECRET = "a-long-enough-secret-for-testing-0123456789"


def test_secret_is_read_from_its_environment_variable(monkeypatch, tmp_path):
    from app_secrets import load_secret

    monkeypatch.setenv("SOME_SECRET", SECRET)

    assert load_secret("SOME_SECRET", tmp_path / "unused") == SECRET


def test_short_secret_is_rejected(monkeypatch, tmp_path):
    from app_secrets import load_secret

    monkeypatch.setenv("SOME_SECRET", "too-short")

    with pytest.raises(ValueError, match="SOME_SECRET must be at least 32"):
        load_secret("SOME_SECRET", tmp_path / "unused")


def test_missing_secret_stops_a_postgres_deployment(monkeypatch, tmp_path):
    from app_secrets import load_secret

    key_file = tmp_path / ".some_secret"
    monkeypatch.delenv("SOME_SECRET", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql://app:pw@db.example.com/trains")

    with pytest.raises(RuntimeError, match="SOME_SECRET is not set"):
        load_secret("SOME_SECRET", key_file)
    assert not key_file.exists()


def test_local_sqlite_generates_a_key_file_and_reuses_it(monkeypatch, tmp_path):
    from app_secrets import load_secret

    key_file = tmp_path / ".some_secret"
    monkeypatch.delenv("SOME_SECRET", raising=False)
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./local.db")

    first = load_secret("SOME_SECRET", key_file)

    assert key_file.read_text().strip() == first
    assert len(first) >= 32
    assert load_secret("SOME_SECRET", key_file) == first
