"""Audit log service."""
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
