"""Borrowings API endpoints."""
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
