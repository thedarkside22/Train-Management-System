"""
encryption_migration.py - Upgrade for databases created before passenger data
was encrypted.

main.py calls this on every startup. It only does work when it finds something
to upgrade, so running it again is harmless:

1. adds the "*_hash" blind index columns if they are missing
2. widens the encrypted columns on PostgreSQL (ciphertext is longer than plaintext)
3. checks that the configured key can read the data that is already encrypted
4. encrypts rows that are still plaintext and fills in their blind indexes
5. creates the indexes that keep national IDs and emails unique
"""

from sqlalchemy import inspect, text

from encryption import CIPHERTEXT_LENGTH, get_cipher

ENCRYPTED_FIELDS = ("national_id", "email", "phone")


def migrate_passenger_encryption(engine, cipher=None):
    cipher = cipher or get_cipher()
    with engine.begin() as conn:
        _add_missing_columns(conn)
        _check_key_reads_existing_data(conn, cipher)
        _encrypt_plaintext_rows(conn, cipher)
        conn.execute(text(
            "CREATE UNIQUE INDEX IF NOT EXISTS ix_passengers_national_id_hash ON passengers (national_id_hash)"
        ))
        conn.execute(text(
            "CREATE UNIQUE INDEX IF NOT EXISTS ix_passengers_email_hash ON passengers (email_hash)"
        ))
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_passengers_phone_hash ON passengers (phone_hash)"
        ))


def _add_missing_columns(conn):
    columns = {column["name"]: column for column in inspect(conn).get_columns("passengers")}
    is_postgres = conn.dialect.name == "postgresql"
    # Two workers may start at once on PostgreSQL; IF NOT EXISTS lets the second one carry on.
    if_not_exists = "IF NOT EXISTS " if is_postgres else ""

    for field in ENCRYPTED_FIELDS:
        if f"{field}_hash" not in columns:
            conn.execute(text(f"ALTER TABLE passengers ADD COLUMN {if_not_exists}{field}_hash VARCHAR(64)"))
        # SQLite does not enforce VARCHAR lengths, so only PostgreSQL needs widening.
        if is_postgres and (columns[field]["type"].length or 0) < CIPHERTEXT_LENGTH:
            conn.execute(text(
                f"ALTER TABLE passengers ALTER COLUMN {field} TYPE VARCHAR({CIPHERTEXT_LENGTH})"
            ))


def _check_key_reads_existing_data(conn, cipher):
    """Stop at startup, rather than on the first request, if the key is the wrong one."""
    encrypted = conn.execute(text(
        "SELECT national_id FROM passengers WHERE national_id_hash IS NOT NULL LIMIT 1"
    )).scalar()
    if encrypted is not None:
        cipher.decrypt(encrypted)


def _encrypt_plaintext_rows(conn, cipher):
    # A row without a blind index was written before encryption existed.
    plaintext_rows = conn.execute(text(
        "SELECT id, national_id, email, phone FROM passengers WHERE national_id_hash IS NULL"
    )).mappings().all()

    for row in plaintext_rows:
        values = {"id": row["id"]}
        for field in ENCRYPTED_FIELDS:
            plaintext = row[field]
            values[field] = None if plaintext is None else cipher.encrypt(plaintext)
            values[f"{field}_hash"] = None if plaintext is None else cipher.blind_index(field, plaintext)
        conn.execute(
            text(
                "UPDATE passengers SET "
                "national_id = :national_id, national_id_hash = :national_id_hash, "
                "email = :email, email_hash = :email_hash, "
                "phone = :phone, phone_hash = :phone_hash "
                "WHERE id = :id"
            ),
            values,
        )
