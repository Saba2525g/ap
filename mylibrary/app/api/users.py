"""Users API (admin only)."""
from __future__ import annotations

from flask import Blueprint, jsonify, request
from app.api._helpers import _error, api_auth_required
from app.extensions import db
from app.models.user import User, VALID_ROLES

bp = Blueprint("api_users", __name__, url_prefix="/api/v1/users")


def _u(u: User) -> dict:
    return {
        "id": u.id, "email": u.email, "full_name": u.full_name,
        "role": u.role, "is_active": u.is_active,
    }


@bp.route("", methods=["GET"])
@bp.route("/", methods=["GET"])
@api_auth_required("admin")
def list_users():
    users = db.session.query(User).order_by(User.id).all()
    return jsonify({"items": [_u(u) for u in users], "total": len(users)})


@bp.route("/<int:uid>", methods=["GET"])
@api_auth_required("admin")
def get_user(uid):
    u = db.session.get(User, uid)
    if not u:
        return _error("not found", 404)
    return jsonify(_u(u))


@bp.route("/<int:uid>", methods=["PUT"])
@api_auth_required("admin")
def update_user(uid):
    u = db.session.get(User, uid)
    if not u:
        return _error("not found", 404)
    data = request.get_json(silent=True) or {}
    if "role" in data:
        if data["role"] not in VALID_ROLES:
            return _error("invalid role", 400)
        u.role = data["role"]
    if "is_active" in data:
        u.is_active = bool(data["is_active"])
    db.session.commit()
    return jsonify(_u(u))
