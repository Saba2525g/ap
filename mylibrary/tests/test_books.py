"""Tests for book catalog and management."""
from app.models.book import Book, Category, Author


def test_catalog_public(client, sample_book):
    r = client.get("/books/")
    assert r.status_code == 200


def test_book_detail_public(client, sample_book):
    r = client.get(f"/books/{sample_book['id']}")
    assert r.status_code == 200


def test_book_404(client):
    r = client.get("/books/99999")
    assert r.status_code == 404


def test_staff_can_create_book(client, admin_user, app):
    client.post("/auth/login", data={"email": admin_user["email"], "password": admin_user["password"]})
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
    client.post("/auth/login", data={"email": student_user["email"], "password": student_user["password"]})
    r = client.get("/books/new", follow_redirects=False)
    assert r.status_code == 403


def test_search_by_title(client, app, admin_user):
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
    client.post("/auth/login", data={"email": admin_user["email"], "password": admin_user["password"]})
    r = client.post("/books/new", data={
        "title": "Dup",
        "isbn": "111-111",
        "total_copies": 1,
        "language": "fa",
    }, follow_redirects=True)
    assert "ISBN".encode() in r.data or "already".encode() in r.data.lower()
