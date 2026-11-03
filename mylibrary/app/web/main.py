"""Main web routes: dashboard."""
from __future__ import annotations

from flask import Blueprint, render_template
from flask_login import current_user

from app.extensions import db
from app.models.book import Book
from app.models.borrowing import Borrowing, Reservation
from app.models.user import User

bp = Blueprint("web_main", __name__)


@bp.route("/")
def index():
    stats = {
        "total_books": db.session.query(Book).count(),
        "available_books": db.session.query(Book).filter(Book.available_copies > 0).count(),
        "total_users": db.session.query(User).count(),
    }

    if current_user.is_authenticated:
        if current_user.is_student and current_user.student:
            stats["my_active"] = db.session.query(Borrowing).filter(
                Borrowing.student_id == current_user.student.id,
                Borrowing.status.in_(["active", "overdue", "pending"]),
            ).count()
            stats["my_overdue"] = db.session.query(Borrowing).filter(
                Borrowing.student_id == current_user.student.id,
                Borrowing.status == "overdue",
            ).count()
        if current_user.role in ("admin", "employee"):
            stats["pending_requests"] = db.session.query(Borrowing).filter(
                Borrowing.status == "pending"
            ).count()
            stats["active_loans"] = db.session.query(Borrowing).filter(
                Borrowing.status.in_(["active", "overdue"])
            ).count()

    return render_template("dashboard.html", stats=stats)