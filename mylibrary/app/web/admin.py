"""Admin routes: audit log."""
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
