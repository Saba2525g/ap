"""Password hashing & verification helpers (bcrypt)."""
from __future__ import annotations
import bcrypt

BCRYPT_ROUNDS = 12
MAX_PASSWORD_BYTES = 72

def hash_password(plain: str) -> str:
    if not plain:
        raise ValueError("password must not be empty")
    raw = plain.encode("utf-8")
    if len(raw) > MAX_PASSWORD_BYTES:
        raw = raw[:MAX_PASSWORD_BYTES]
    return bcrypt.hashpw(raw, bcrypt.gensalt(rounds=BCRYPT_ROUNDS)).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    if not plain or not hashed:
        return False
    try:
        raw = plain.encode("utf-8")[:MAX_PASSWORD_BYTES]
        return bcrypt.checkpw(raw, hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False
