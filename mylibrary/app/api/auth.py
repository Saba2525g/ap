"""Auth API endpoints."""
from __future__ import annotations

from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest

from app.auth.services import AuthError, register_student
from app.extensions import db
from app.models.user import User
from app.utils.jwt_helpers import create_access_token
from app.utils.security import verify_password
from app.api._helpers import _error, api_auth_required

bp = Blueprint("api_auth", __name__, url_prefix="/api/v1/auth")


def _user_json(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "role": u.role,
        "phone": u.phone,
        "is_active": u.is_active,
    }


@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    required = ["full_name", "email", "password", "student_number"]
    missing = [k for k in required if not data.get(k)]
    if missing:
        return _error(f"Missing fields: {', '.join(missing)}", 400, "missing_fields")
    try:
        user = register_student(
            full_name=data["full_name"],
            email=data["email"],
            password=data["password"],
            student_number=data["student_number"],
            phone=data.get("phone"),
            faculty=data.get("faculty"),
            major=data.get("major"),
            enrollment_year=data.get("enrollment_year"),
        )
    except AuthError as e:
        return _error(str(e), 400, "register_failed")
    token = create_access_token(user.id, user.role)
    return jsonify({"user": _user_json(user), "access_token": token, "token_type": "bearer"}), 201


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not email or not password:
        return _error("email and password are required", 400, "missing_fields")
    user = db.session.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return _error("Invalid credentials", 401, "invalid_credentials")
    user.touch_login()
    db.session.commit()
    token = create_access_token(user.id, user.role)
    return jsonify({"user": _user_json(user), "access_token": token, "token_type": "bearer"})


@bp.route("/me", methods=["GET"])
@api_auth_required()
def me():
    return jsonify({"user": _user_json(request.current_user)})


@bp.route("/logout", methods=["POST"])
@api_auth_required()
def logout():
    # JWT is stateless; client should discard token
    return jsonify({"message": "logged out"})
