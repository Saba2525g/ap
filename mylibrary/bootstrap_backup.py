"""Write backup/restore service, routes, and templates."""
import os

FILES = {}

FILES["app/services/backup_service.py"] = '''"""JSON backup and restore service."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from sqlalchemy import inspect

from app.extensions import db
from app.models.book import Author, Book, BookAuthor, Category
from app.models.borrowing import Borrowing, Reservation
from app.models.notification import Notification
from app.models.settings import LibrarySettings
from app.models.user import Employee, Student, User

BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "backups")
SCHEMA_VERSION = 1


class BackupError(Exception):
    pass


def _utcnow_iso():
    return datetime.now(timezone.utc).isoformat()


def _ensure_dir():
    os.makedirs(BACKUP_DIR, exist_ok=True)


def _serialize_row(row, model):
    out = {}
    mapper = inspect(model)
    for col in mapper.columns:
        v = getattr(row, col.key, None)
        if isinstance(v, datetime):
            v = v.isoformat()
        out[col.key] = v
    return out


def export_data(include_users=True, include_passwords=False):
    _ensure_dir()
    def rows(model):
        return [_serialize_row(r, model) for r in db.session.query(model).all()]
    data = {
        "schema_version": SCHEMA_VERSION,
        "exported_at": _utcnow_iso(),
        "data": {
            "users": rows(User) if include_users else [],
            "students": rows(Student) if include_users else [],
            "employees": rows(Employee) if include_users else [],
            "categories": rows(Category),
            "authors": rows(Author),
            "books": rows(Book),
            "book_authors": rows(BookAuthor),
            "borrowings": rows(Borrowing),
            "reservations": rows(Reservation),
            "notifications": rows(Notification),
            "library_settings": rows(LibrarySettings),
        },
    }
    if not include_passwords:
        for u in data["data"]["users"]:
            u.pop("password_hash", None)
    return data


def save_backup_file(data):
    _ensure_dir()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"backup_{ts}.json"
    path = os.path.join(BACKUP_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


def list_backups():
    _ensure_dir()
    items = []
    for fn in sorted(os.listdir(BACKUP_DIR), reverse=True):
        if not fn.endswith(".json"):
            continue
        path = os.path.join(BACKUP_DIR, fn)
        stat = os.stat(path)
        items.append({
            "filename": fn,
            "size": stat.st_size,
            "size_kb": round(stat.st_size / 1024, 1),
            "modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        })
    return items


def load_backup_file(filename):
    safe = os.path.basename(filename)
    path = os.path.join(BACKUP_DIR, safe)
    if not os.path.exists(path):
        raise BackupError(f"file not found: {safe}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def validate_backup(data):
    problems = []
    if not isinstance(data, dict):
        return ["not a JSON object"]
    if data.get("schema_version") != SCHEMA_VERSION:
        problems.append("invalid schema version")
    if "data" not in data or not isinstance(data["data"], dict):
        problems.append("missing data")
        return problems
    for key in ["books", "authors", "categories", "borrowings", "reservations"]:
        if key not in data["data"]:
            problems.append(f"missing table {key}")
    return problems


def restore_from_data(data, wipe_before=False, skip_existing=True):
    problems = validate_backup(data)
    if problems:
        raise BackupError(" | ".join(problems))
    stats = {"created": {}, "skipped": {}}
    d = data["data"]
    try:
        if wipe_before:
            db.session.query(Borrowing).delete()
            db.session.query(Reservation).delete()
            db.session.query(BookAuthor).delete()
            db.session.query(Book).delete()
            db.session.query(Author).delete()
            db.session.query(Category).delete()
            db.session.query(Notification).delete()
            db.session.flush()
        for table_key, model in [("categories", Category), ("authors", Author), ("books", Book)]:
            stats["created"][table_key] = 0
            for row in d.get(table_key, []):
                if skip_existing and db.session.get(model, row.get("id")):
                    stats["skipped"][table_key] = stats["skipped"].get(table_key, 0) + 1
                    continue
                clean = {k: v for k, v in row.items() if k not in ("id", "created_at", "updated_at")}
                db.session.merge(model(**clean))
                db.session.flush()
                stats["created"][table_key] += 1
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise BackupError(f"restore failed: {e}")
    return stats
'''

FILES["app/templates/admin/backup.html"] = """{% extends 'base.html' %}
{% block title %}Backup | MyLibrary{% endblock %}
{% block content %}
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem; flex-wrap:wrap; gap:1rem;">
  <h1 style="font-size:1.8rem;">Backup و Restore</h1>
  <a href="{{ url_for('web_admin.backup_restore') }}" class="btn btn-gold">بازیابی</a>
</div>
<div class="glass" style="padding:1.75rem; margin-bottom:1.5rem;">
  <h2 style="margin-bottom:.75rem;">ایجاد بکاپ جدید</h2>
  <form method="POST" action="{{ url_for('web_admin.backup_export') }}">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <label style="display:flex; align-items:center; gap:.5rem; margin-bottom:1rem;">
      <input type="checkbox" name="include_passwords" value="1">
      شامل رمزها (معمولا نیاز نیست)
    </label>
    <button type="submit" class="btn btn-gold">ساخت بکاپ</button>
  </form>
</div>
<h2 style="font-size:1.2rem; margin-bottom:.8rem;">بکاپ‌های موجود</h2>
{% if backups %}
  <div style="background:#fff; border-radius:12px; overflow:hidden;">
    <table class="data-table">
      <thead><tr><th>فایل</th><th>حجم</th><th>تاریخ</th><th>عملیات</th></tr></thead>
      <tbody>
        {% for b in backups %}
          <tr>
            <td>{{ b.filename }}</td>
            <td>{{ b.size_kb }} KB</td>
            <td>{{ b.modified[:19] }}</td>
            <td><a href="{{ url_for('web_admin.backup_download', filename=b.filename) }}" class="btn btn-sm btn-primary">دانلود</a></td>
          </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
{% else %}
  <div class="glass" style="padding:2rem; text-align:center; color:var(--gray-500);">هنوز بکاپی ساخته نشده.</div>
{% endif %}
{% endblock %}
"""

FILES["app/templates/admin/backup_restore.html"] = """{% extends 'base.html' %}
{% block title %}Restore | MyLibrary{% endblock %}
{% block content %}
<div style="max-width:720px; margin:0 auto;">
  <h1 style="font-size:1.8rem; margin-bottom:1rem;">بازیابی (Restore)</h1>
  <form method="POST" enctype="multipart/form-data" class="glass" style="padding:1.75rem;">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <div class="form-group">
      <label>منبع</label>
      <select name="source" class="form-control" id="src" onchange="toggleSrc()">
        <option value="upload">آپلود</option>
        <option value="existing">از موجود</option>
      </select>
    </div>
    <div class="form-group" id="up">
      <label>فایل JSON</label>
      <input type="file" name="file" accept=".json" class="form-control">
    </div>
    <div class="form-group" id="ex" style="display:none;">
      <label>بکاپ</label>
      <select name="filename" class="form-control">
        <option value="">-</option>
        {% for b in backups %}<option value="{{ b.filename }}">{{ b.filename }}</option>{% endfor %}
      </select>
    </div>
    <label style="display:flex; gap:.5rem; color:var(--danger); margin:1rem 0;">
      <input type="checkbox" name="wipe_before" value="1"> پاک کردن همه قبل از restore
    </label>
    <button type="submit" class="btn btn-gold" onclick="return confirm('مطمئنید؟');">شروع</button>
    <a href="{{ url_for('web_admin.backup_index') }}" class="btn btn-ghost">بازگشت</a>
  </form>
</div>
<script>
function toggleSrc() {
  const v = document.getElementById('src').value;
  document.getElementById('up').style.display = v === 'upload' ? 'block' : 'none';
  document.getElementById('ex').style.display = v === 'existing' ? 'block' : 'none';
}
</script>
{% endblock %}
"""

FILES["app/web/admin.py"] = '''"""Admin routes: audit, backup."""
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
'''

for path, content in FILES.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"WROTE {path} ({len(content)} bytes)")

print("\nDONE: 4 files written.")
