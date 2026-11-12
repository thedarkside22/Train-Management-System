"""Upgrading a database that was created before passenger data was encrypted."""

import os
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

BACKEND_DIR = Path(__file__).resolve().parents[1]
OTHER_SECRET = "a-different-secret-than-the-test-run-uses-0123456789"

# The passengers table exactly as the app created it before encryption.
LEGACY_SCHEMA = """
CREATE TABLE passengers (
    id INTEGER NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    national_id VARCHAR(10) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(15) NOT NULL,
    created_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
    PRIMARY KEY (id),
    UNIQUE (email)
)
"""
LEGACY_ROWS = [
    {"id": 1, "full_name": "Sara Alharbi", "national_id": "1100000001",
     "email": "sara@example.com", "phone": "0501111111"},
    {"id": 2, "full_name": "Omar Saleh", "national_id": "2200000002",
     "email": None, "phone": "0502222222"},
]
PERSONAL_VALUES = ["1100000001", "sara@example.com", "0501111111", "2200000002", "0502222222"]


def _build_legacy_db(path):
    engine = create_engine(f"sqlite:///{path}")
    with engine.begin() as conn:
        conn.execute(text(LEGACY_SCHEMA))
        conn.execute(text("CREATE UNIQUE INDEX ix_passengers_national_id ON passengers (national_id)"))
        conn.execute(
            text("INSERT INTO passengers (id, full_name, national_id, email, phone) "
                 "VALUES (:id, :full_name, :national_id, :email, :phone)"),
            LEGACY_ROWS,
        )
    return engine


def _rows(engine):
    with engine.connect() as conn:
        return [dict(r) for r in conn.execute(text("SELECT * FROM passengers ORDER BY id")).mappings()]


@pytest.fixture()
def legacy_engine(tmp_path):
    engine = _build_legacy_db(tmp_path / "legacy.db")
    yield engine
    engine.dispose()


def test_existing_plaintext_rows_get_encrypted(legacy_engine):
    from encryption_migration import migrate_passenger_encryption

    migrate_passenger_encryption(legacy_engine)

    stored = " ".join(str(value) for row in _rows(legacy_engine) for value in row.values())
    for personal_value in PERSONAL_VALUES:
        assert personal_value not in stored


def test_encrypted_rows_decrypt_back_to_the_original_values(legacy_engine):
    from encryption import decrypt
    from encryption_migration import migrate_passenger_encryption

    migrate_passenger_encryption(legacy_engine)

    sara, omar = _rows(legacy_engine)
    assert decrypt(sara["national_id"]) == "1100000001"
    assert decrypt(sara["email"]) == "sara@example.com"
    assert decrypt(sara["phone"]) == "0501111111"
    assert decrypt(omar["national_id"]) == "2200000002"
    assert omar["email"] is None


def test_blind_indexes_are_filled_in(legacy_engine):
    from encryption import blind_index
    from encryption_migration import migrate_passenger_encryption

    migrate_passenger_encryption(legacy_engine)

    sara, omar = _rows(legacy_engine)
    assert sara["national_id_hash"] == blind_index("national_id", "1100000001")
    assert sara["email_hash"] == blind_index("email", "sara@example.com")
    assert sara["phone_hash"] == blind_index("phone", "0501111111")
    assert omar["email_hash"] is None


def test_upgraded_passengers_can_be_found_and_read_through_the_model(legacy_engine):
    from encryption import blind_index
    from encryption_migration import migrate_passenger_encryption
    from models import Passenger

    migrate_passenger_encryption(legacy_engine)

    with Session(legacy_engine) as db:
        sara = db.query(Passenger).filter(
            Passenger.national_id_hash == blind_index("national_id", "1100000001")
        ).one()
        assert sara.full_name == "Sara Alharbi"
        assert sara.national_id == "1100000001"
        assert sara.phone == "0501111111"
        assert sara.email == "sara@example.com"


def test_new_passengers_can_be_added_after_the_upgrade(legacy_engine):
    from encryption_migration import migrate_passenger_encryption
    from models import Passenger

    migrate_passenger_encryption(legacy_engine)

    with Session(legacy_engine) as db:
        db.add(Passenger(full_name="Noura Ali", national_id="1300000003", phone="0503333333"))
        db.commit()

    assert len(_rows(legacy_engine)) == 3


def test_running_the_upgrade_twice_changes_nothing(legacy_engine):
    from encryption_migration import migrate_passenger_encryption

    migrate_passenger_encryption(legacy_engine)
    after_first_run = _rows(legacy_engine)
    migrate_passenger_encryption(legacy_engine)

    assert _rows(legacy_engine) == after_first_run


def test_upgrade_refuses_to_run_with_a_different_key(legacy_engine):
    from encryption import FieldCipher, WrongKeyError
    from encryption_migration import migrate_passenger_encryption

    migrate_passenger_encryption(legacy_engine)

    with pytest.raises(WrongKeyError):
        migrate_passenger_encryption(legacy_engine, FieldCipher(OTHER_SECRET))


def test_upgraded_database_rejects_a_duplicate_national_id(legacy_engine):
    from encryption_migration import migrate_passenger_encryption
    from models import Passenger

    migrate_passenger_encryption(legacy_engine)

    with Session(legacy_engine) as db:
        db.add(Passenger(full_name="Copy", national_id="1100000001", phone="0504444444"))
        with pytest.raises(IntegrityError):
            db.commit()


def test_starting_the_app_upgrades_a_legacy_database(tmp_path):
    db_path = tmp_path / "legacy_app.db"
    _build_legacy_db(db_path).dispose()
    env = {**os.environ, "DATABASE_URL": f"sqlite:///{db_path.as_posix()}"}

    started = subprocess.run(
        [sys.executable, "-c", "import main"],
        cwd=BACKEND_DIR, env=env, capture_output=True, text=True, timeout=120,
    )

    assert started.returncode == 0, started.stderr
    engine = create_engine(f"sqlite:///{db_path}")
    try:
        stored = " ".join(str(value) for row in _rows(engine) for value in row.values())
    finally:
        engine.dispose()
    for personal_value in PERSONAL_VALUES:
        assert personal_value not in stored
