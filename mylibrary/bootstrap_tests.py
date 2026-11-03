"""Write all pytest test files."""
import os

FILES = {}

FILES["tests/__init__.py"] = '"""Tests package."""\n'

FILES["tests/conftest.py"] = '''"""Pytest fixtures for MyLibrary tests."""
import os
import sys
import tempfile

import pytest

# Make sure project root is on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import create_app
from app.extensions import db as _db
from app.models.user import User, Student, Employee, ROLE_STUDENT, ROLE_EMPLOYEE, ROLE_ADMIN
from app.models.book import Author, Book, BookAuthor, Category


@pytest.fixture
def app():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    uri = f"sqlite:///{path}"
    os.environ["TEST_DATABASE_URL"] = uri

    app = create_app("testing")
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()
    os.unlink(path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    return _db


@pytest.fixture
def admin_user(app):
    with app.app_context():
        u = User(email="admin@test.com", full_name="Admin Test", role=ROLE_ADMIN, is_active=True)
        u.set_password("adminpass123")
        _db.session.add(u)
        _db.session.commit()
        return u


@pytest.fixture
def student_user(app):
    with app.app_context():
        u = User(email="student@test.com", full_name="Student Test", role=ROLE_STUDENT, is_active=True)
        u.set_password("student123")
        _db.session.add(u)
        _db.session.flush()
        s = Student(user_id=u.id, student_number="99001", faculty="Eng", major="CS", enrollment_year=1402)
        _db.session.add(s)
        _db.session.commit()
        return u


@pytest.fixture
def employee_user(app):
    with app.app_context():
        u = User(email="emp@test.com", full_name="Employee Test", role=ROLE_EMPLOYEE, is_active=True)
        u.set_password("emppass123")
        _db.session.add(u)
        _db.session.flush()
        e = Employee(user_id=u.id, employee_number="E001", department="Library", position="Librarian")
        _db.session.add(e)
        _db.session.commit()
        return u


@pytest.fixture
def sample_book(app):
    with app.app_context():
        cat = Category(name="Test Cat", slug="test-cat")
        _db.session.add(cat)
        _db.session.flush()
        a = Author(full_name="Test Author")
        _db.session.add(a)
        _db.session.flush()
        b = Book(title="Test Book", isbn="111-111", total_copies=3,
                 available_copies=3, category_id=cat.id, is_active=True)
        _db.session.add(b)
        _db.session.flush()
        _db.session.add(BookAuthor(book_id=b.id, author_id=a.id, position=1))
        _db.session.commit()
        return b
'''

FILES["tests/test_auth.py"] = '''"""Tests for authentication and authorization."""
from app.models.user import User


def test_home_page(client):
    r = client.get("/")
    assert r.status_code == 200


def test_login_page_loads(client):
    r = client.get("/auth/login")
    assert r.status_code == 200
    assert b"login" in r.data.lower() or "ورود".encode() in r.data


def test_register_student_success(client, app):
    r = client.post("/auth/register", data={
        "full_name": "New Student",
        "email": "new@test.com",
        "student_number": "88001",
        "password": "Passw0rd!",
        "confirm": "Passw0rd!",
    }, follow_redirects=True)
    assert r.status_code == 200
    with app.app_context():
        u = User.query.filter_by(email="new@test.com").first()
        assert u is not None
        assert u.role == "student"
        assert u.student is not None
        assert u.student.student_number == "88001"


def test_register_duplicate_email(client, student_user):
    r = client.post("/auth/register", data={
        "full_name": "Dup",
        "email": "student@test.com",
        "student_number": "88002",
        "password": "Passw0rd!",
        "confirm": "Passw0rd!",
    }, follow_redirects=True)
    assert "قبلاً" in r.data.decode() or "already" in r.data.decode().lower()


def test_register_password_mismatch(client):
    r = client.post("/auth/register", data={
        "full_name": "Mismatch",
        "email": "mm@test.com",
        "student_number": "88003",
        "password": "Passw0rd!",
        "confirm": "Different!",
    }, follow_redirects=True)
    assert r.status_code == 200


def test_login_success(client, student_user):
    r = client.post("/auth/login", data={
        "email": "student@test.com",
        "password": "student123",
    }, follow_redirects=True)
    assert r.status_code == 200
    assert "خوش آمدید".encode() in r.data or b"student" in r.data.lower()


def test_login_wrong_password(client, student_user):
    r = client.post("/auth/login", data={
        "email": "student@test.com",
        "password": "wrongpass",
    }, follow_redirects=True)
    assert "اشتباه".encode() in r.data or "invalid".encode() in r.data.lower()


def test_login_nonexistent_user(client):
    r = client.post("/auth/login", data={
        "email": "nope@test.com",
        "password": "anything",
    }, follow_redirects=True)
    assert r.status_code == 200


def test_password_hashing():
    from app.models.user import User
    u = User(email="hash@test.com", full_name="H", role="student")
    u.set_password("mypassword")
    assert u.password_hash != "mypassword"
    assert u.check_password("mypassword")
    assert not u.check_password("wrongpass")


def test_protected_route_redirects_anonymous(client):
    r = client.get("/borrowings/my", follow_redirects=False)
    assert r.status_code in (302, 401)


def test_role_required_forbidden(client, student_user):
    client.post("/auth/login", data={"email": "student@test.com", "password": "student123"})
    r = client.get("/borrowings/requests", follow_redirects=False)
    assert r.status_code == 403


def test_admin_can_access_audit(client, admin_user):
    client.post("/auth/login", data={"email": "admin@test.com", "password": "adminpass123"})
    r = client.get("/admin/audit")
    assert r.status_code == 200
'''

FILES["tests/test_books.py"] = '''"""Tests for book catalog and management."""
from app.models.book import Book, Category, Author


def test_catalog_public(client, sample_book):
    r = client.get("/books/")
    assert r.status_code == 200


def test_book_detail_public(client, sample_book, app):
    r = client.get(f"/books/{sample_book.id}")
    assert r.status_code == 200


def test_book_404(client):
    r = client.get("/books/99999")
    assert r.status_code == 404


def test_staff_can_create_book(client, admin_user, app):
    client.post("/auth/login", data={"email": "admin@test.com", "password": "adminpass123"})
    r = client.post("/books/new", data={
        "title": "New Test Book",
        "isbn": "222-333",
        "total_copies": 2,
        "language": "fa",
    }, follow_redirects=True)
    assert r.status_code == 200
    with app.app_context():
        b = Book.query.filter_by(isbn="222-333").first()
        assert b is not None
        assert b.title == "New Test Book"


def test_student_cannot_create_book(client, student_user):
    client.post("/auth/login", data={"email": "student@test.com", "password": "student123"})
    r = client.get("/books/new", follow_redirects=False)
    assert r.status_code == 403


def test_search_by_title(client, app):
    with app.app_context():
        c = Category(name="C", slug="c")
        app.extensions["sqlalchemy"].session.add(c)
        app.extensions["sqlalchemy"].session.flush()
        b = Book(title="Unique Title Xyz", isbn="999-999", total_copies=1,
                 available_copies=1, category_id=c.id)
        app.extensions["sqlalchemy"].session.add(b)
        app.extensions["sqlalchemy"].session.commit()
    r = client.get("/books/?q=Unique")
    assert r.status_code == 200
    assert b"Unique Title Xyz" in r.data


def test_duplicate_isbn_rejected(client, admin_user, sample_book, app):
    client.post("/auth/login", data={"email": "admin@test.com", "password": "adminpass123"})
    r = client.post("/books/new", data={
        "title": "Dup",
        "isbn": "111-111",
        "total_copies": 1,
        "language": "fa",
    }, follow_redirects=True)
    assert "ISBN".encode() in r.data or "already".encode() in r.data.lower()
'''

FILES["tests/test_borrowings.py"] = '''"""Tests for borrowing workflow."""
from app.models.borrowing import Borrowing, STATUS_ACTIVE, STATUS_PENDING, STATUS_RETURNED
from app.models.book import Book


def _login(client, email, pw):
    return client.post("/auth/login", data={"email": email, "password": pw}, follow_redirects=True)


def test_student_can_request_borrow(client, student_user, sample_book, app):
    _login(client, "student@test.com", "student123")
    r = client.post(f"/borrowings/request/{sample_book.id}", follow_redirects=True)
    assert r.status_code == 200
    with app.app_context():
        b = Borrowing.query.filter_by(student_id=student_user.student.id).first()
        assert b is not None
        assert b.status == STATUS_PENDING


def test_employee_can_approve(client, employee_user, student_user, sample_book, app):
    _login(client, "student@test.com", "student123")
    client.post(f"/borrowings/request/{sample_book.id}", follow_redirects=True)
    with app.app_context():
        b = Borrowing.query.first()
        bid = b.id

    client.get("/auth/logout")
    _login(client, "emp@test.com", "emppass123")
    r = client.post(f"/borrowings/{bid}/approve", follow_redirects=True)
    assert r.status_code == 200

    with app.app_context():
        b = Borrowing.query.get(bid)
        assert b.status == STATUS_ACTIVE
        book = Book.query.get(sample_book.id)
        assert book.available_copies == 2  # 3 - 1


def test_employee_can_reject(client, employee_user, student_user, sample_book, app):
    _login(client, "student@test.com", "student123")
    client.post(f"/borrowings/request/{sample_book.id}", follow_redirects=True)
    with app.app_context():
        bid = Borrowing.query.first().id
    client.get("/auth/logout")
    _login(client, "emp@test.com", "emppass123")
    r = client.post(f"/borrowings/{bid}/reject", data={"reason": "test"},
                    follow_redirects=True)
    assert r.status_code == 200


def test_employee_can_return(client, employee_user, student_user, sample_book, app):
    _login(client, "student@test.com", "student123")
    client.post(f"/borrowings/request/{sample_book.id}", follow_redirects=True)
    with app.app_context():
        bid = Borrowing.query.first().id
    client.get("/auth/logout")
    _login(client, "emp@test.com", "emppass123")
    client.post(f"/borrowings/{bid}/approve", follow_redirects=True)
    r = client.post(f"/borrowings/{bid}/return", follow_redirects=True)
    assert r.status_code == 200

    with app.app_context():
        b = Borrowing.query.get(bid)
        assert b.status == STATUS_RETURNED
        book = Book.query.get(sample_book.id)
        assert book.available_copies == 3  # back to original
'''

FILES["tests/test_api.py"] = '''"""Tests for REST API."""
import json


def _login_api(client, email, pw):
    r = client.post("/api/v1/auth/login", json={"email": email, "password": pw})
    return r


def test_api_login_success(client, admin_user):
    r = _login_api(client, "admin@test.com", "adminpass123")
    assert r.status_code == 200
    data = r.get_json()
    assert "access_token" in data
    assert data["user"]["email"] == "admin@test.com"


def test_api_login_fail(client, admin_user):
    r = _login_api(client, "admin@test.com", "wrong")
    assert r.status_code == 401


def test_api_me_requires_token(client):
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 401


def test_api_me_success(client, admin_user):
    r = _login_api(client, "admin@test.com", "adminpass123")
    token = r.get_json()["access_token"]
    r2 = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    assert r2.get_json()["user"]["email"] == "admin@test.com"


def test_api_books_public(client, sample_book):
    r = client.get("/api/v1/books")
    assert r.status_code == 200
    data = r.get_json()
    assert "items" in data
    assert len(data["items"]) >= 1


def test_api_stats_global(client, sample_book):
    r = client.get("/api/v1/stats/global")
    assert r.status_code == 200
    data = r.get_json()
    assert "total_books" in data
    assert data["total_books"] >= 1


def test_api_create_book_requires_auth(client):
    r = client.post("/api/v1/books", json={"title": "X", "isbn": "Y"})
    assert r.status_code == 401


def test_api_admin_can_create_book(client, admin_user):
    r = _login_api(client, "admin@test.com", "adminpass123")
    token = r.get_json()["access_token"]
    r2 = client.post("/api/v1/books",
                     json={"title": "API Book", "isbn": "API-1", "total_copies": 2},
                     headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 201
    assert r2.get_json()["isbn"] == "API-1"


def test_api_student_cannot_create_book(client, student_user):
    r = _login_api(client, "student@test.com", "student123")
    token = r.get_json()["access_token"]
    r2 = client.post("/api/v1/books", json={"title": "X", "isbn": "Y"},
                     headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 403
'''

FILES["tests/test_backup.py"] = '''"""Tests for backup/restore service."""
from app.services import backup_service as bk
from app.models.book import Book


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
        loaded = bk.load_backup_file(path.split("/")[-1].split("\\\\")[-1])
        assert loaded["schema_version"] == 1


def test_validate_bad_data():
    problems = bk.validate_backup({"schema_version": 999})
    assert problems


def test_validate_good_data(app, sample_book):
    with app.app_context():
        data = bk.export_data()
        problems = bk.validate_backup(data)
        assert problems == []
'''

for path, content in FILES.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"WROTE {path} ({len(content)} bytes)")

print("\nDONE: 7 test files written.")
