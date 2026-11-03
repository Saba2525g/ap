"""Admin routes: audit, backup."""
from __future__ import annotations

import json
import os

from flask import (Blueprint, abort, flash, redirect, render_template,
                   request, send_file, url_for)
from flask_login import current_user

from app.auth.decorators import admin_required
from app.extensions import db
from app.models.audit_log import AuditLog
from app.services import audit_service
from app.services import backup_service as bk

bp = Blueprint("web_admin", __name__, url_prefix="/admin")


@bp.route("/audit")
@admin_required
def audit_list():
    items = audit_service.recent(limit=200)
    return render_template("admin/audit.html", items=items)


@bp.route("/audit/<int:entry_id>")
@admin_required
def audit_detail(entry_id):
    entry = db.session.get(AuditLog, entry_id)
    if not entry:
        abort(404)
    return render_template("admin/audit_detail.html", entry=entry)


@bp.route("/backup")
@admin_required
def backup_index():
    backups = bk.list_backups()
    return render_template("admin/backup.html", backups=backups)


@bp.route("/backup/export", methods=["POST"])
@admin_required
def backup_export():
    include_passwords = request.form.get("include_passwords") == "1"
    data = bk.export_data(include_passwords=include_passwords)
    path = bk.save_backup_file(data)
    audit_service.log_action(
        user=current_user, action="backup.export", entity_type="backup",
        details=os.path.basename(path), request=request,
    )
    flash("backup created: " + os.path.basename(path), "success")
    return redirect(url_for("web_admin.backup_index"))


@bp.route("/backup/download/<path:filename>")
@admin_required
def backup_download(filename):
    safe = os.path.basename(filename)
    path = os.path.join(bk.BACKUP_DIR, safe)
    if not os.path.exists(path):
        abort(404)
    return send_file(path, as_attachment=True, download_name=safe)


@bp.route("/backup/restore", methods=["GET", "POST"])
@admin_required
def backup_restore():
    if request.method == "POST":
        source = request.form.get("source", "upload")
        wipe = request.form.get("wipe_before") == "1"
        try:
            if source == "existing":
                filename = request.form.get("filename", "").strip()
                if not filename:
                    raise bk.BackupError("no filename")
                data = bk.load_backup_file(filename)
            else:
                f = request.files.get("file")
                if not f or not f.filename:
                    raise bk.BackupError("no file")
                data = json.loads(f.read().decode("utf-8"))
            stats = bk.restore_from_data(data, wipe_before=wipe)
            audit_service.log_action(
                user=current_user, action="backup.restore", entity_type="backup",
                details=json.dumps(stats), request=request,
            )
            flash("restore done", "success")
            return redirect(url_for("web_admin.backup_index"))
        except (bk.BackupError, json.JSONDecodeError) as e:
            flash("error: " + str(e), "danger")
    return render_template("admin/backup_restore.html", backups=bk.list_backups())
