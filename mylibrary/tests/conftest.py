"""Pytest fixtures for MyLibrary tests."""
import os
import sys
import tempfile

import pytest

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
    """Returns a dict with user id + email (detached-safe)."""
    with app.app_context():
        u = User(email="admin@test.com", full_name="Admin Test", role=ROLE_ADMIN, is_active=True)
        u.set_password("adminpass123")
        _db.session.add(u)
        _db.session.commit()
        return {"id": u.id, "email": u.email, "password": "adminpass123"}


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
        return {"id": u.id, "email": u.email, "password": "student123", "student_id": s.id}


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
        return {"id": u.id, "email": u.email, "password": "emppass123", "employee_id": e.id}


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
        return {"id": b.id, "isbn": b.isbn, "title": b.title, "category_id": cat.id, "author_id": a.id}
