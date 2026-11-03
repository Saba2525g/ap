"""Dashboard statistics and chart data."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func

from app.extensions import db
from app.models.book import Book, Category
from app.models.borrowing import Borrowing, Reservation
from app.models.user import User
from app.models.audit_log import AuditLog


def _utcnow():
    return datetime.now(timezone.utc)


def global_stats() -> dict:
    return {
        "total_books": db.session.query(Book).filter(Book.is_active.is_(True)).count(),
        "available_books": db.session.query(Book).filter(
            Book.is_active.is_(True), Book.available_copies > 0).count(),
        "total_users": db.session.query(User).count(),
        "total_students": db.session.query(User).filter(User.role == "student").count(),
        "active_loans": db.session.query(Borrowing).filter(
            Borrowing.status.in_(["active", "overdue"])).count(),
        "pending_requests": db.session.query(Borrowing).filter(
            Borrowing.status == "pending").count(),
        "overdue_loans": db.session.query(Borrowing).filter(
            Borrowing.status == "overdue").count(),
        "total_reservations": db.session.query(Reservation).filter(
            Reservation.status.in_(["pending", "ready"])).count(),
    }


def student_stats(student) -> dict:
    if not student:
        return {}
    base = db.session.query(Borrowing).filter(Borrowing.student_id == student.id)
    return {
        "my_active": base.filter(Borrowing.status.in_(["active", "overdue"])).count(),
        "my_pending": base.filter(Borrowing.status == "pending").count(),
        "my_overdue": base.filter(Borrowing.status == "overdue").count(),
        "my_returned": base.filter(Borrowing.status == "returned").count(),
        "my_reservations": db.session.query(Reservation).filter(
            Reservation.student_id == student.id,
            Reservation.status.in_(["pending", "ready"])).count(),
    }


def chart_borrowings_7d() -> dict:
    """Bar chart: borrowings requested per day for last 7 days."""
    now = _utcnow()
    labels = []
    counts = []
    for i in range(6, -1, -1):
        day = (now - timedelta(days=i)).date()
        start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
        end = start + timedelta(days=1)
        c = db.session.query(Borrowing).filter(
            Borrowing.requested_at >= start,
            Borrowing.requested_at < end,
        ).count()
        labels.append(day.strftime("%m-%d"))
        counts.append(c)
    return {"labels": labels, "counts": counts}


def chart_category_pie() -> dict:
    """Pie chart: book distribution by category."""
    rows = (db.session.query(Category.name, func.count(Book.id))
            .outerjoin(Book, Book.category_id == Category.id)
            .filter(Book.is_active.is_(True))
            .group_by(Category.id).all())
    labels = [r[0] for r in rows if r[1] > 0]
    counts = [r[1] for r in rows if r[1] > 0]
    if not labels:
        return {"labels": ["بدون دسته"], "counts": [1]}
    return {"labels": labels, "counts": counts}


def chart_borrowing_status() -> dict:
    rows = (db.session.query(Borrowing.status, func.count(Borrowing.id))
            .group_by(Borrowing.status).all())
    return {
        "labels": [r[0] for r in rows],
        "counts": [r[1] for r in rows],
    }


def recent_activities(limit: int = 10):
    return (db.session.query(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .limit(limit).all())


def popular_books(limit: int = 5):
    rows = (db.session.query(Book.title, func.count(Borrowing.id).label("cnt"))
            .join(Borrowing, Borrowing.book_id == Book.id)
            .group_by(Book.id)
            .order_by(func.count(Borrowing.id).desc())
            .limit(limit).all())
    return [{"title": r[0], "count": r[1]} for r in rows]


def overdue_list(limit: int = 20):
    return (db.session.query(Borrowing)
            .filter(Borrowing.status == "overdue")
            .order_by(Borrowing.due_date)
            .limit(limit).all())
