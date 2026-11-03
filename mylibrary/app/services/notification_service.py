"""Notification service."""
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
