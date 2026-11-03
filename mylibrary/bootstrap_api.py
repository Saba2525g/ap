"""Write complete REST API under /api/v1/."""
import os

FILES = {}

FILES["app/api/__init__.py"] = '''"""REST API v1."""
from app.api.auth import bp as auth_bp
from app.api.books import bp as books_bp
from app.api.borrowings import bp as borrowings_bp
from app.api.users import bp as users_bp
from app.api.stats import bp as stats_bp

__all__ = ["auth_bp", "books_bp", "borrowings_bp", "users_bp", "stats_bp"]
'''

FILES["app/api/_helpers.py"] = '''"""Shared API helpers."""
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
'''

FILES["app/utils/jwt_helpers.py"] = '''"""JWT helpers using PyJWT."""
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
'''

FILES["app/api/auth.py"] = '''"""Auth API endpoints."""
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
'''

FILES["app/api/books.py"] = '''"""Books API endpoints."""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.api._helpers import _error, api_auth_required
from app.services import book_service as svc

bp = Blueprint("api_books", __name__, url_prefix="/api/v1/books")


def _book_json(b) -> dict:
    return {
        "id": b.id,
        "title": b.title,
        "isbn": b.isbn,
        "publisher": b.publisher,
        "publish_year": b.publish_year,
        "language": b.language,
        "pages": b.pages,
        "cover_url": b.cover_url,
        "description": b.description,
        "category": ({"id": b.category.id, "name": b.category.name} if b.category else None),
        "authors": [{"id": l.author.id, "name": l.author.full_name} for l in b.author_links if l.author],
        "total_copies": b.total_copies,
        "available_copies": b.available_copies,
        "is_available": b.is_available,
        "is_active": b.is_active,
    }


@bp.route("", methods=["GET"])
@bp.route("/", methods=["GET"])
def list_books():
    q = request.args.get("q")
    cat = request.args.get("category", type=int)
    lang = request.args.get("language")
    avail = request.args.get("available") == "1"
    page = max(1, request.args.get("page", 1, type=int))
    per_page = min(100, request.args.get("per_page", 20, type=int))
    items, total = svc.search_books(
        q=q, category_id=cat, language=lang,
        available_only=avail, limit=per_page, offset=(page - 1) * per_page,
    )
    return jsonify({
        "items": [_book_json(b) for b in items],
        "total": total, "page": page, "per_page": per_page,
        "pages": max(1, (total + per_page - 1) // per_page),
    })


@bp.route("/<int:bid>", methods=["GET"])
def get_book(bid):
    b = svc.get_book(bid)
    if not b:
        return _error("book not found", 404, "not_found")
    return jsonify(_book_json(b))


@bp.route("", methods=["POST"])
@bp.route("/", methods=["POST"])
@api_auth_required("employee", "admin")
def create_book():
    data = request.get_json(silent=True) or {}
    try:
        book = svc.create_book(
            title=data.get("title", ""),
            isbn=data.get("isbn", ""),
            total_copies=int(data.get("total_copies", 1)),
            author_ids=data.get("author_ids") or [],
            category_id=data.get("category_id"),
            description=data.get("description"),
            publisher=data.get("publisher"),
            publish_year=data.get("publish_year"),
            language=data.get("language", "fa"),
            pages=data.get("pages"),
            shelf_location=data.get("shelf_location"),
            cover_url=data.get("cover_url"),
        )
    except (svc.BookError, ValueError) as e:
        return _error(str(e), 400, "invalid_book")
    return jsonify(_book_json(book)), 201


@bp.route("/<int:bid>", methods=["PUT"])
@api_auth_required("employee", "admin")
def update_book(bid):
    b = svc.get_book(bid)
    if not b:
        return _error("book not found", 404, "not_found")
    data = request.get_json(silent=True) or {}
    fields = {k: v for k, v in data.items() if k in {
        "title", "isbn", "publisher", "publish_year", "language", "pages",
        "description", "category_id", "total_copies", "shelf_location", "cover_url", "author_ids"
    }}
    svc.update_book(b, **fields)
    return jsonify(_book_json(b))


@bp.route("/<int:bid>", methods=["DELETE"])
@api_auth_required("employee", "admin")
def delete_book(bid):
    b = svc.get_book(bid)
    if not b:
        return _error("book not found", 404, "not_found")
    svc.delete_book(b)
    return jsonify({"message": "deleted"})
'''

FILES["app/api/borrowings.py"] = '''"""Borrowings API endpoints."""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.api._helpers import _error, api_auth_required
from app.extensions import db
from app.models.borrowing import Borrowing
from app.services import borrowing_service as bsvc
from app.services.book_service import get_book

bp = Blueprint("api_borrowings", __name__, url_prefix="/api/v1/borrowings")


def _b_json(b) -> dict:
    return {
        "id": b.id,
        "status": b.status,
        "student": {"id": b.student.id, "number": b.student.student_number},
        "book": {"id": b.book.id, "title": b.book.title},
        "requested_at": b.requested_at.isoformat() if b.requested_at else None,
        "approved_at": b.approved_at.isoformat() if b.approved_at else None,
        "due_date": b.due_date.isoformat() if b.due_date else None,
        "returned_at": b.returned_at.isoformat() if b.returned_at else None,
        "fine_amount": b.fine_amount,
        "is_overdue": b.is_overdue,
    }


@bp.route("", methods=["GET"])
@bp.route("/", methods=["GET"])
@api_auth_required()
def list_borrowings():
    u = request.current_user
    status = request.args.get("status")
    q = db.session.query(Borrowing)
    if u.role == "student" and u.student:
        q = q.filter(Borrowing.student_id == u.student.id)
    elif u.role not in ("employee", "admin"):
        return _error("Forbidden", 403, "forbidden")
    if status:
        q = q.filter(Borrowing.status == status)
    items = q.order_by(Borrowing.requested_at.desc()).limit(200).all()
    return jsonify({"items": [_b_json(b) for b in items], "total": len(items)})


@bp.route("/<int:bid>", methods=["GET"])
@api_auth_required()
def get_borrowing(bid):
    b = db.session.get(Borrowing, bid)
    if not b:
        return _error("not found", 404)
    u = request.current_user
    if u.role == "student" and (not u.student or b.student_id != u.student.id):
        return _error("forbidden", 403, "forbidden")
    return jsonify(_b_json(b))


@bp.route("", methods=["POST"])
@bp.route("/", methods=["POST"])
@api_auth_required("student")
def create_borrowing():
    data = request.get_json(silent=True) or {}
    book_id = data.get("book_id")
    if not book_id:
        return _error("book_id required", 400)
    book = get_book(int(book_id))
    if not book:
        return _error("book not found", 404)
    u = request.current_user
    try:
        b = bsvc.request_borrow(u.student, book)
    except bsvc.BorrowError as e:
        return _error(str(e), 400, "borrow_failed")
    return jsonify(_b_json(b)), 201


@bp.route("/<int:bid>/approve", methods=["POST"])
@api_auth_required("employee", "admin")
def approve(bid):
    b = db.session.get(Borrowing, bid)
    if not b:
        return _error("not found", 404)
    try:
        bsvc.approve_borrow(b, request.current_user)
    except bsvc.BorrowError as e:
        return _error(str(e), 400)
    return jsonify(_b_json(b))


@bp.route("/<int:bid>/reject", methods=["POST"])
@api_auth_required("employee", "admin")
def reject(bid):
    b = db.session.get(Borrowing, bid)
    if not b:
        return _error("not found", 404)
    data = request.get_json(silent=True) or {}
    try:
        bsvc.reject_borrow(b, request.current_user, data.get("reason", ""))
    except bsvc.BorrowError as e:
        return _error(str(e), 400)
    return jsonify(_b_json(b))


@bp.route("/<int:bid>/return", methods=["POST"])
@api_auth_required("employee", "admin")
def return_book(bid):
    b = db.session.get(Borrowing, bid)
    if not b:
        return _error("not found", 404)
    try:
        bsvc.return_book(b, request.current_user)
    except bsvc.BorrowError as e:
        return _error(str(e), 400)
    return jsonify(_b_json(b))
'''

FILES["app/api/users.py"] = '''"""Users API (admin only)."""
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
'''

FILES["app/api/stats.py"] = '''"""Stats API endpoints."""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.api._helpers import api_auth_required
from app.services import dashboard_service as dash

bp = Blueprint("api_stats", __name__, url_prefix="/api/v1/stats")


@bp.route("/global", methods=["GET"])
def global_stats():
    return jsonify(dash.global_stats())


@bp.route("/charts", methods=["GET"])
def charts():
    return jsonify({
        "borrowings_7d": dash.chart_borrowings_7d(),
        "category_pie": dash.chart_category_pie(),
        "status_breakdown": dash.chart_borrowing_status(),
    })


@bp.route("/me", methods=["GET"])
@api_auth_required()
def me_stats():
    u = request.current_user
    if u.is_student and u.student:
        return jsonify(dash.student_stats(u.student))
    return jsonify({})
'''

FILES["app/templates/api/docs.html"] = """{% extends 'base.html' %}
{% block title %}API Docs | MyLibrary{% endblock %}
{% block content %}
<div style="text-align:center; margin-bottom:2rem;">
  <h1 style="font-size:2rem;">API Documentation</h1>
  <p style="color:var(--gray-500);">MyLibrary REST API v1 — JWT Authentication</p>
</div>

<div class="glass" style="padding:2rem; margin-bottom:1rem;">
  <h2 style="margin-bottom:1rem;">Authentication</h2>
  <p style="color:var(--gray-500); margin-bottom:1rem;">All protected endpoints require: <code style="background:#0b1120;color:#e2c25a;padding:.2rem .5rem;border-radius:6px;">Authorization: Bearer &lt;token&gt;</code></p>
  <p>Get a token via <code>POST /api/v1/auth/login</code> with body:</p>
  <pre style="background:#0b1120;color:#a7f3d0;padding:1rem;border-radius:8px;overflow:auto;">{"email": "...", "password": "..."}</pre>
</div>

<div class="glass" style="padding:2rem;">
  <h2 style="margin-bottom:1rem;">Endpoints</h2>

  <h3 style="margin:1.5rem 0 .5rem; color:var(--gold-600);">Auth</h3>
  <table class="data-table">
    <tr><th>Method</th><th>Path</th><th>Description</th></tr>
    <tr><td>POST</td><td>/api/v1/auth/register</td><td>ثبت‌نام دانشجو</td></tr>
    <tr><td>POST</td><td>/api/v1/auth/login</td><td>ورود</td></tr>
    <tr><td>GET</td><td>/api/v1/auth/me</td><td>اطلاعات کاربر</td></tr>
  </table>

  <h3 style="margin:1.5rem 0 .5rem; color:var(--gold-600);">Books</h3>
  <table class="data-table">
    <tr><th>Method</th><th>Path</th><th>Description</th></tr>
    <tr><td>GET</td><td>/api/v1/books?q=&category=&page=</td><td>لیست کتاب‌ها</td></tr>
    <tr><td>GET</td><td>/api/v1/books/&lt;id&gt;</td><td>جزئیات</td></tr>
    <tr><td>POST</td><td>/api/v1/books</td><td>ایجاد (staff)</td></tr>
    <tr><td>PUT</td><td>/api/v1/books/&lt;id&gt;</td><td>ویرایش (staff)</td></tr>
    <tr><td>DELETE</td><td>/api/v1/books/&lt;id&gt;</td><td>حذف (staff)</td></tr>
  </table>

  <h3 style="margin:1.5rem 0 .5rem; color:var(--gold-600);">Borrowings</h3>
  <table class="data-table">
    <tr><th>Method</th><th>Path</th><th>Description</th></tr>
    <tr><td>GET</td><td>/api/v1/borrowings</td><td>لیست امانت‌ها</td></tr>
    <tr><td>POST</td><td>/api/v1/borrowings</td><td>درخواست امانت</td></tr>
    <tr><td>POST</td><td>/api/v1/borrowings/&lt;id&gt;/approve</td><td>تأیید (staff)</td></tr>
    <tr><td>POST</td><td>/api/v1/borrowings/&lt;id&gt;/reject</td><td>رد (staff)</td></tr>
    <tr><td>POST</td><td>/api/v1/borrowings/&lt;id&gt;/return</td><td>بازگشت (staff)</td></tr>
  </table>

  <h3 style="margin:1.5rem 0 .5rem; color:var(--gold-600);">Users (admin)</h3>
  <table class="data-table">
    <tr><th>Method</th><th>Path</th><th>Description</th></tr>
    <tr><td>GET</td><td>/api/v1/users</td><td>لیست کاربران</td></tr>
    <tr><td>PUT</td><td>/api/v1/users/&lt;id&gt;</td><td>تغییر نقش</td></tr>
  </table>

  <h3 style="margin:1.5rem 0 .5rem; color:var(--gold-600);">Stats</h3>
  <table class="data-table">
    <tr><th>Method</th><th>Path</th><th>Description</th></tr>
    <tr><td>GET</td><td>/api/v1/stats/global</td><td>آمار کلی</td></tr>
    <tr><td>GET</td><td>/api/v1/stats/charts</td><td>داده نمودارها</td></tr>
    <tr><td>GET</td><td>/api/v1/stats/me</td><td>آمار من</td></tr>
  </table>
</div>
{% endblock %}
"""

for path, content in FILES.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"WROTE {path} ({len(content)} bytes)")

print("\nDONE: 10 API files written.")
