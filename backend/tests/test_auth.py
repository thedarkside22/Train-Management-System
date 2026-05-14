def test_register_and_login(client):
    r = client.post("/api/auth/register", json={
        "username": "alice",
        "email": "alice@example.com",
        "password": "Password1",
        "full_name": "Alice",
        "role": "staff",
    })
    assert r.status_code == 201

    r = client.post("/api/auth/login", data={"username": "alice", "password": "Password1"})
    assert r.status_code == 200
    body = r.json()
    assert body["role"] == "staff"
    assert body["access_token"]


def test_login_wrong_password_rejected(client):
    client.post("/api/auth/register", json={
        "username": "bob", "email": "bob@example.com",
        "password": "Password1", "full_name": "Bob", "role": "staff",
    })
    r = client.post("/api/auth/login", data={"username": "bob", "password": "WrongPassw0rd"})
    assert r.status_code == 401


def test_protected_route_requires_token(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 401
