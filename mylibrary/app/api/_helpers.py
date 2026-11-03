"""Shared API helpers."""
from __future__ import annotations

from functools import wraps
from flask import jsonify, request
from app.utils.jwt_helpers import decode_token
from app.extensions import db
from app.models.user import User


def _error(message: str, status: int = 400, code: str = "bad_request"):
    return jsonify({"error": {"code": code, "message": message}}), status


def api_auth_required(*allowed_roles):
    """Decorator for JSON APIs. Reads Authorization: Bearer <token>."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            auth = request.headers.get("Authorization", "")
            if not auth.startswith("Bearer "):
                return _error("Missing or invalid Authorization header", 401, "unauthorized")
            token = auth[7:].strip()
            try:
                payload = decode_token(token)
            except Exception as e:
                return _error(f"Invalid token: {e}", 401, "invalid_token")
            user = db.session.get(User, int(payload["sub"]))
            if not user or not user.is_active:
                return _error("User not found or inactive", 401, "unauthorized")
            if allowed_roles and user.role not in allowed_roles:
                return _error("Forbidden", 403, "forbidden")
            request.current_user = user
            return view_func(*args, **kwargs)
        return wrapped
    return decorator
