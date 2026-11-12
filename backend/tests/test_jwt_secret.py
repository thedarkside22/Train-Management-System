"""The JWT signing key comes from the environment, not from the source code."""

import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt

BACKEND_DIR = Path(__file__).resolve().parents[1]

# The key that used to be written in auth.py. It is in the public git history,
# so anyone can sign tokens with it.
OLD_PUBLISHED_KEY = "6733f17dd5dfb3556969e21d544bc1c2e50cab07667e5093c09c4af49afd3709"


def _import_auth(**env_changes):
    """Import auth.py in a fresh process. A value of None removes that variable."""
    env = {**os.environ}
    for name, value in env_changes.items():
        if value is None:
            env.pop(name, None)
        else:
            env[name] = value
    return subprocess.run(
        [sys.executable, "-c", "import auth"],
        cwd=BACKEND_DIR, env=env, capture_output=True, text=True, timeout=120,
    )


def test_tokens_are_signed_with_the_secret_from_the_environment():
    from auth import create_access_token

    token = create_access_token({"user_id": 1})

    payload = jwt.decode(token, os.environ["SECRET_KEY"], algorithms=["HS256"])
    assert payload["user_id"] == 1


def test_token_forged_with_the_old_published_key_is_rejected(client, admin_headers):
    me = client.get("/api/auth/me", headers=admin_headers).json()
    forged = jwt.encode(
        {"sub": me["username"], "user_id": me["id"], "role": "admin",
         "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
        OLD_PUBLISHED_KEY, algorithm="HS256",
    )

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {forged}"})

    assert response.status_code == 401


def test_app_refuses_to_start_on_postgres_without_a_jwt_secret():
    started = _import_auth(SECRET_KEY=None, DATABASE_URL="postgresql://app:pw@db.example.com/trains")

    assert started.returncode != 0
    assert "SECRET_KEY is not set" in started.stderr


def test_app_refuses_to_start_with_the_old_published_key():
    started = _import_auth(SECRET_KEY=OLD_PUBLISHED_KEY)

    assert started.returncode != 0
    assert "published" in started.stderr
