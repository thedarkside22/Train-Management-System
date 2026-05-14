def test_admin_can_create_train(client, admin_headers):
    r = client.post("/api/trains/", headers=admin_headers, json={
        "name": "HARAMAIN-1", "train_type": "High Speed", "total_seats": 300, "status": "active",
    })
    assert r.status_code == 201
    assert r.json()["name"] == "HARAMAIN-1"


def test_staff_cannot_create_train(client, staff_headers):
    r = client.post("/api/trains/", headers=staff_headers, json={
        "name": "X", "train_type": "Local", "total_seats": 100,
    })
    assert r.status_code in (403, 422)


def test_train_listing_paginates(client, admin_headers):
    for i in range(3):
        client.post("/api/trains/", headers=admin_headers, json={
            "name": f"T-{i}", "train_type": "Local", "total_seats": 50,
        })
    r = client.get("/api/trains/?per_page=2", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["per_page"] == 2
    assert body["total"] >= 3
    assert len(body["items"]) <= 2
