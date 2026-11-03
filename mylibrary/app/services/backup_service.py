"""JSON backup and restore service."""
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
