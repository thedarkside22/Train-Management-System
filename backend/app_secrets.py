"""
app_secrets.py - Loads secrets from the environment, never from the code.

A real deployment (anything that is not SQLite) must set each secret as an
environment variable, and the app refuses to start without it. For local
SQLite development a key file is created on first use, so the app runs
without any setup. Those files are listed in .gitignore.
"""

import os
import secrets
import sys
from pathlib import Path

MIN_SECRET_LENGTH = 32


def load_secret(env_var: str, local_file: Path) -> str:
    secret = os.getenv(env_var)
    if secret:
        if len(secret) < MIN_SECRET_LENGTH:
            raise ValueError(f"{env_var} must be at least {MIN_SECRET_LENGTH} characters long")
        return secret

    database_url = os.getenv("DATABASE_URL", "sqlite:///./train_system.db")
    if not database_url.startswith("sqlite"):
        raise RuntimeError(
            f"{env_var} is not set. "
            'Generate one with: python -c "import secrets; print(secrets.token_urlsafe(48))"'
        )

    if local_file.exists():
        return local_file.read_text().strip()

    secret = secrets.token_urlsafe(48)
    local_file.write_text(secret)
    print(
        f"WARNING: {env_var} is not set. Generated a local development key in "
        f"{local_file}. Do not commit it and do not use it in production.",
        file=sys.stderr,
    )
    return secret
