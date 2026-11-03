"""Tests for backup/restore service."""
from app.services import backup_service as bk


def test_export_returns_dict(app, sample_book):
    with app.app_context():
        data = bk.export_data()
        assert isinstance(data, dict)
        assert data["schema_version"] == 1
        assert "data" in data
        assert "books" in data["data"]
        assert len(data["data"]["books"]) >= 1


def test_export_no_passwords_by_default(app, admin_user):
    with app.app_context():
        data = bk.export_data()
        for u in data["data"]["users"]:
            assert "password_hash" not in u


def test_save_and_load_backup(app, sample_book):
    with app.app_context():
        data = bk.export_data()
        path = bk.save_backup_file(data)
        assert path.endswith(".json")
        fname = path.split("/")[-1].split("\\")[-1]
        loaded = bk.load_backup_file(fname)
        assert loaded["schema_version"] == 1


def test_validate_bad_data():
    problems = bk.validate_backup({"schema_version": 999})
    assert problems


def test_validate_good_data(app, sample_book):
    with app.app_context():
        data = bk.export_data()
        problems = bk.validate_backup(data)
        assert problems == []
