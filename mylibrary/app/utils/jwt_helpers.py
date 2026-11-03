"""JWT helpers using PyJWT."""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import jwt

JWT_SECRET = os.environ.get("SECRET_KEY", "dev-only-insecure-key-change-me")
JWT_ALG = "HS256"
ACCESS_TOKEN_TTL = timedelta(hours=12)


def create_access_token(user_id: int, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + ACCESS_TOKEN_TTL).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
