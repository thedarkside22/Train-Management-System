"""Passenger personal data is encrypted in the database but unchanged through the API."""

import pytest
from sqlalchemy import text

PASSENGER = {
    "full_name": "Sara Alharbi",
    "national_id": "1100000001",
    "email": "sara@example.com",
    "phone": "0501111111",
}


def _create(client, headers, **overrides):
    return client.post("/api/passengers/", headers=headers, json={**PASSENGER, **overrides})


def _stored_row(passenger_id):
    """The row exactly as the database holds it, bypassing the ORM."""
    from database import engine

    with engine.connect() as conn:
        return conn.execute(
            text("SELECT * FROM passengers WHERE id = :id"), {"id": passenger_id}
        ).mappings().one()


def _search(client, headers, term):
    return client.get("/api/passengers/", headers=headers, params={"search": term}).json()


def test_personal_fields_are_not_stored_in_plaintext(client, admin_headers):
    created = _create(client, admin_headers).json()

    stored = " ".join(str(value) for value in _stored_row(created["id"]).values())

    for personal_value in ("1100000001", "0501111111", "sara@example.com"):
        assert personal_value not in stored


def test_api_returns_the_original_values(client, admin_headers):
    created = _create(client, admin_headers).json()

    fetched = client.get(f"/api/passengers/{created['id']}", headers=admin_headers).json()

    assert fetched["national_id"] == "1100000001"
    assert fetched["phone"] == "0501111111"
    assert fetched["email"] == "sara@example.com"


def test_duplicate_national_id_is_rejected(client, admin_headers):
    _create(client, admin_headers)

    again = _create(client, admin_headers, email="other@example.com")

    assert again.status_code == 409


def test_duplicate_email_is_rejected(client, admin_headers):
    _create(client, admin_headers)

    again = _create(client, admin_headers, national_id="1100000002")

    assert again.status_code == 409


def test_two_passengers_without_email_are_allowed(client, admin_headers):
    first = _create(client, admin_headers, email=None)
    second = _create(client, admin_headers, national_id="1100000002", email=None)

    assert first.status_code == 201
    assert second.status_code == 201


def test_lookup_by_national_id_finds_the_passenger(client, admin_headers):
    created = _create(client, admin_headers).json()

    found = client.get("/api/passengers/national-id/1100000001", headers=admin_headers)

    assert found.status_code == 200
    assert found.json()["id"] == created["id"]


def test_lookup_by_unknown_national_id_returns_404(client, admin_headers):
    _create(client, admin_headers)

    found = client.get("/api/passengers/national-id/1999999999", headers=admin_headers)

    assert found.status_code == 404


def test_search_finds_passenger_by_exact_national_id(client, admin_headers):
    _create(client, admin_headers)

    assert _search(client, admin_headers, "1100000001")["total"] == 1


def test_search_finds_passenger_by_exact_phone(client, admin_headers):
    _create(client, admin_headers)

    assert _search(client, admin_headers, "0501111111")["total"] == 1


def test_search_finds_passenger_by_partial_name(client, admin_headers):
    _create(client, admin_headers)

    assert _search(client, admin_headers, "alhar")["total"] == 1


def test_search_does_not_match_part_of_a_national_id(client, admin_headers):
    _create(client, admin_headers)

    assert _search(client, admin_headers, "110000")["total"] == 0


def test_database_rejects_a_second_row_with_the_same_national_id(client):
    from sqlalchemy.exc import IntegrityError

    from database import SessionLocal
    from models import Passenger

    db = SessionLocal()
    try:
        db.add(Passenger(full_name="First", national_id="1100000001", phone="0501111111"))
        db.commit()
        db.add(Passenger(full_name="Second", national_id="1100000001", phone="0502222222"))
        with pytest.raises(IntegrityError):
            db.commit()
    finally:
        db.rollback()
        db.close()


def test_filtering_on_an_encrypted_column_is_refused():
    from models import Passenger

    with pytest.raises(TypeError, match="_hash"):
        Passenger.national_id == "1100000001"
