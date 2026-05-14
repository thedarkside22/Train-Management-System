"""Shared pytest fixtures. Spins up an isolated SQLite DB per test session."""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# tests/ -> backend/
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session", autouse=True)
def _isolated_db():
    """Use a throwaway sqlite file for the whole test run."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.environ["DATABASE_URL"] = f"sqlite:///{path}"
    yield
    try:
        os.remove(path)
    except OSError:
        pass


@pytest.fixture()
def client(_isolated_db):
    from fastapi.testclient import TestClient
    from database import Base, engine
    from main import app

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with TestClient(app) as c:
        yield c


def _register_and_login(client, role: str = "admin", username: str = "admin1") -> str:
    payload = {
        "username": username,
        "email": f"{username}@example.com",
        "password": "Password1",
        "full_name": "Test User",
        "role": role,
    }
    client.post("/api/auth/register", json=payload)
    resp = client.post(
        "/api/auth/login",
        data={"username": username, "password": "Password1"},
    )
    return resp.json()["access_token"]


@pytest.fixture()
def admin_token(client) -> str:
    return _register_and_login(client, "admin", "admin1")


@pytest.fixture()
def staff_token(client) -> str:
    return _register_and_login(client, "staff", "staff1")


@pytest.fixture()
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture()
def staff_headers(staff_token):
    return {"Authorization": f"Bearer {staff_token}"}
