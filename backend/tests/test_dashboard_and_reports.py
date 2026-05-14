"""Sprint 3 - dashboard, reports and analytics endpoint tests."""

from datetime import date, timedelta


def _setup_data(client, admin_headers):
    train = client.post("/api/trains/", headers=admin_headers, json={
        "name": "DASH-TRAIN", "train_type": "High Speed", "total_seats": 5, "status": "active",
    }).json()
    dep = (date.today() + timedelta(days=10)).isoformat()
    sched = client.post("/api/schedules/", headers=admin_headers, json={
        "train_id": train["id"], "origin": "Riyadh", "destination": "Dammam",
        "departure_date": dep, "departure_time": "07:00:00", "arrival_time": "10:00:00",
        "ticket_price": 150.0,
    }).json()
    p1 = client.post("/api/passengers/", headers=admin_headers, json={
        "full_name": "P One", "national_id": "1100000001",
        "email": "p1@x.com", "phone": "0501111111",
    }).json()
    client.post("/api/reservations/", headers=admin_headers, json={
        "passenger_id": p1["id"], "schedule_id": sched["id"],
    })
    return train, sched


def test_dashboard_stats(client, admin_headers):
    _setup_data(client, admin_headers)
    r = client.get("/api/dashboard/stats", headers=admin_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total_trains"] >= 1
    assert body["total_passengers"] >= 1
    assert body["confirmed_reservations"] >= 1
    assert body["bookings_today"] >= 1
    assert body["revenue_today"] >= 150.0


def test_dashboard_requires_admin(client, staff_headers):
    r = client.get("/api/dashboard/stats", headers=staff_headers)
    assert r.status_code == 403


def test_revenue_trend_returns_n_points(client, admin_headers):
    _setup_data(client, admin_headers)
    r = client.get("/api/dashboard/revenue-trend?days=7", headers=admin_headers)
    assert r.status_code == 200
    assert len(r.json()) == 7


def test_report_generation_json(client, admin_headers):
    _setup_data(client, admin_headers)
    r = client.get("/api/reports/?period=daily", headers=admin_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["period"] == "daily"
    assert body["total_bookings"] >= 1


def test_report_csv_export(client, admin_headers):
    _setup_data(client, admin_headers)
    r = client.get("/api/reports/export/csv?period=weekly", headers=admin_headers)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/csv")
    assert b"Total Bookings" in r.content


def test_report_pdf_export(client, admin_headers):
    _setup_data(client, admin_headers)
    r = client.get("/api/reports/export/pdf?period=monthly", headers=admin_headers)
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content[:4] == b"%PDF"


def test_passenger_booking_history(client, admin_headers):
    _setup_data(client, admin_headers)
    p = client.get("/api/passengers/national-id/1100000001", headers=admin_headers).json()
    r = client.get(f"/api/passengers/{p['id']}/bookings", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["summary"]["total_bookings"] >= 1
    assert body["bookings"][0]["origin"] == "Riyadh"


def test_analytics_eda(client, admin_headers):
    _setup_data(client, admin_headers)
    r = client.get("/api/analytics/eda", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["rows"] >= 1
    assert "by_status" in body


def test_analytics_features(client, admin_headers):
    _setup_data(client, admin_headers)
    r = client.get("/api/analytics/features?limit=5", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["rows"] >= 1
    assert "dep_dayofweek" in body["columns"]
    assert "lead_time_days" in body["columns"]
