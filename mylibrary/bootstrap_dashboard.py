"""Write dashboard backend files."""
import os

FILES = {}

FILES["app/services/audit_service.py"] = '''"""Audit log service."""
from __future__ import annotations

from app.extensions import db
from app.models.audit_log import AuditLog


def log_action(*, user=None, action: str, entity_type: str | None = None,
               entity_id: int | None = None, details: str | None = None,
               request=None) -> AuditLog:
    ip = None
    ua = None
    if request is not None:
        try:
            ip = request.headers.get("X-Forwarded-For", request.remote_addr)
            ua = (request.headers.get("User-Agent") or "")[:300]
        except Exception:
            pass
    entry = AuditLog(
        actor_id=getattr(user, "id", None) if user else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        ip_address=ip,
        user_agent=ua,
    )
    db.session.add(entry)
    db.session.commit()
    return entry


def recent(limit: int = 50):
    return (db.session.query(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .limit(limit).all())
'''

FILES["app/services/notification_service.py"] = '''"""Notification service."""
from __future__ import annotations

from datetime import datetime, timezone

from app.extensions import db
from app.models.notification import Notification


def notify(user_id: int, title: str, message: str,
           category: str = "info", link: str | None = None) -> Notification:
    n = Notification(user_id=user_id, title=title, message=message,
                     category=category, link=link)
    db.session.add(n)
    db.session.commit()
    return n


def unread_count(user_id: int) -> int:
    return (db.session.query(Notification)
            .filter(Notification.user_id == user_id,
                    Notification.is_read.is_(False))
            .count())


def list_for_user(user_id: int, limit: int = 100):
    return (db.session.query(Notification)
            .filter(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit).all())


def mark_read(notification_id: int, user_id: int) -> bool:
    n = db.session.get(Notification, notification_id)
    if not n or n.user_id != user_id:
        return False
    n.mark_read()
    db.session.commit()
    return True


def mark_all_read(user_id: int) -> int:
    now = datetime.now(timezone.utc)
    count = (db.session.query(Notification)
             .filter(Notification.user_id == user_id,
                     Notification.is_read.is_(False))
             .update({"is_read": True, "read_at": now},
                     synchronize_session=False))
    db.session.commit()
    return count
'''

FILES["app/services/dashboard_service.py"] = '''"""Dashboard statistics and chart data."""
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
'''

FILES["app/web/notifications.py"] = '''"""Notification routes."""
from __future__ import annotations

from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.services import notification_service as svc

bp = Blueprint("web_notifications", __name__, url_prefix="/notifications")


@bp.route("/")
@login_required
def list_all():
    items = svc.list_for_user(current_user.id)
    unread = svc.unread_count(current_user.id)
    return render_template("notifications/list.html", items=items, unread=unread)


@bp.route("/<int:nid>/read", methods=["POST"])
@login_required
def mark_read(nid: int):
    svc.mark_read(nid, current_user.id)
    return redirect(request.referrer or url_for("web_notifications.list_all"))


@bp.route("/read-all", methods=["POST"])
@login_required
def read_all():
    svc.mark_all_read(current_user.id)
    return redirect(url_for("web_notifications.list_all"))


@bp.route("/api/unread-count")
@login_required
def api_unread_count():
    return jsonify({"count": svc.unread_count(current_user.id)})
'''

FILES["app/web/admin.py"] = '''"""Admin routes: audit log."""
from __future__ import annotations

from flask import Blueprint, abort, render_template
from flask_login import login_required

from app.auth.decorators import admin_required
from app.extensions import db
from app.models.audit_log import AuditLog
from app.services import audit_service

bp = Blueprint("web_admin", __name__, url_prefix="/admin")


@bp.route("/audit")
@admin_required
def audit_list():
    items = audit_service.recent(limit=200)
    return render_template("admin/audit.html", items=items)


@bp.route("/audit/<int:entry_id>")
@admin_required
def audit_detail(entry_id: int):
    entry = db.session.get(AuditLog, entry_id)
    if not entry:
        abort(404)
    return render_template("admin/audit_detail.html", entry=entry)
'''

FILES["app/web/main.py"] = '''"""Main dashboard route."""
from __future__ import annotations

from flask import Blueprint, render_template
from flask_login import current_user

from app.services import dashboard_service as dash

bp = Blueprint("web_main", __name__)


@bp.route("/")
def index():
    stats = dash.global_stats()
    chart_7d = dash.chart_borrowings_7d()
    chart_cat = dash.chart_category_pie()
    chart_status = dash.chart_borrowing_status()
    popular = dash.popular_books(5)

    student_stats_data = {}
    if current_user.is_authenticated and current_user.is_student and current_user.student:
        student_stats_data = dash.student_stats(current_user.student)

    recent = []
    if current_user.is_authenticated and current_user.role in ("admin", "employee"):
        recent = dash.recent_activities(10)

    return render_template(
        "dashboard.html",
        stats=stats,
        student_stats=student_stats_data,
        chart_7d=chart_7d,
        chart_cat=chart_cat,
        chart_status=chart_status,
        popular=popular,
        recent=recent,
    )
'''

for path, content in FILES.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"WROTE {path} ({len(content)} bytes)")

print("\nDONE: 6 backend files written.")
