"""Integration tests for the end-to-end booking flow (Sprint 3 - TESTING)."""

from datetime import date, timedelta


def _make_train(client, headers, name="T1", seats=2):
    r = client.post("/api/trains/", headers=headers, json={
        "name": name, "train_type": "High Speed", "total_seats": seats, "status": "active",
    })
    assert r.status_code == 201
    return r.json()["id"]


def _make_schedule(client, headers, train_id, days_ahead=10, price=200.0):
    dep = (date.today() + timedelta(days=days_ahead)).isoformat()
    r = client.post("/api/schedules/", headers=headers, json={
        "train_id": train_id,
        "origin": "Riyadh",
        "destination": "Jeddah",
        "departure_date": dep,
        "departure_time": "08:00:00",
        "arrival_time": "12:00:00",
        "ticket_price": price,
    })
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _make_passenger(client, headers, national_id="1000000001"):
    r = client.post("/api/passengers/", headers=headers, json={
        "full_name": "Passenger One",
        "national_id": national_id,
        "email": f"p{national_id}@x.com",
        "phone": "0501234567",
    })
    assert r.status_code == 201, r.text
    return r.json()["id"]


def test_book_then_cancel_releases_seat(client, admin_headers):
    train_id = _make_train(client, admin_headers, name="HARAMAIN", seats=2)
    sched_id = _make_schedule(client, admin_headers, train_id, days_ahead=14, price=100.0)
    pid = _make_passenger(client, admin_headers, "1000000010")

    # before booking
    s = client.get(f"/api/schedules/{sched_id}", headers=admin_headers).json()
    assert s["available_seats"] == 2

    r = client.post("/api/reservations/", headers=admin_headers, json={
        "passenger_id": pid, "schedule_id": sched_id,
    })
    assert r.status_code == 201, r.text
    booking_ref = r.json()["booking_reference"]

    s = client.get(f"/api/schedules/{sched_id}", headers=admin_headers).json()
    assert s["available_seats"] == 1

    # cancel via reference -> id lookup
    res = client.get(f"/api/reservations/ref/{booking_ref}", headers=admin_headers).json()
    cancel = client.delete(f"/api/reservations/{res['id']}", headers=admin_headers)
    assert cancel.status_code == 200, cancel.text
    body = cancel.json()
    assert body["refund_percentage"] == 1.0  # 14 days out -> full refund
    assert body["refund_amount"] == 100.0

    # seat returned
    s = client.get(f"/api/schedules/{sched_id}", headers=admin_headers).json()
    assert s["available_seats"] == 2


def test_cannot_overbook(client, admin_headers):
    train_id = _make_train(client, admin_headers, name="LOCAL", seats=1)
    sched_id = _make_schedule(client, admin_headers, train_id, days_ahead=5, price=80.0)
    p1 = _make_passenger(client, admin_headers, "1000000020")
    p2 = _make_passenger(client, admin_headers, "1000000021")

    r1 = client.post("/api/reservations/", headers=admin_headers, json={"passenger_id": p1, "schedule_id": sched_id})
    assert r1.status_code == 201

    r2 = client.post("/api/reservations/", headers=admin_headers, json={"passenger_id": p2, "schedule_id": sched_id})
    assert r2.status_code == 400


def test_cancel_idempotency(client, admin_headers):
    train_id = _make_train(client, admin_headers, name="EXPRESS", seats=2)
    sched_id = _make_schedule(client, admin_headers, train_id, days_ahead=10, price=50.0)
    pid = _make_passenger(client, admin_headers, "1000000030")
    r = client.post("/api/reservations/", headers=admin_headers, json={"passenger_id": pid, "schedule_id": sched_id})
    res_id = client.get(f"/api/reservations/ref/{r.json()['booking_reference']}", headers=admin_headers).json()["id"]

    assert client.delete(f"/api/reservations/{res_id}", headers=admin_headers).status_code == 200
    # second cancel should be a 409
    assert client.delete(f"/api/reservations/{res_id}", headers=admin_headers).status_code == 409
