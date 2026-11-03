"""Tests for borrowing workflow."""
from app.models.borrowing import Borrowing, STATUS_ACTIVE, STATUS_PENDING, STATUS_RETURNED
from app.models.book import Book


def _login(client, email, pw):
    return client.post("/auth/login", data={"email": email, "password": pw}, follow_redirects=True)


def _logout(client):
    """Logout MUST be POST."""
    return client.post("/auth/logout", follow_redirects=True)


def test_student_can_request_borrow(client, student_user, sample_book, app):
    _login(client, student_user["email"], student_user["password"])
    r = client.post("/borrowings/request/" + str(sample_book["id"]), follow_redirects=True)
    assert r.status_code == 200
    with app.app_context():
        b = Borrowing.query.filter_by(student_id=student_user["student_id"]).first()
        assert b is not None
        assert b.status == STATUS_PENDING


def test_employee_can_approve(client, employee_user, student_user, sample_book, app):
    _login(client, student_user["email"], student_user["password"])
    client.post("/borrowings/request/" + str(sample_book["id"]), follow_redirects=True)
    with app.app_context():
        bid = Borrowing.query.first().id
    _logout(client)
    _login(client, employee_user["email"], employee_user["password"])

    with client.session_transaction() as sess:
        assert sess.get("_user_id") == str(employee_user["id"]), f"session user is {sess.get('_user_id')}, expected {employee_user['id']}"

    r = client.post("/borrowings/" + str(bid) + "/approve", follow_redirects=True)
    assert r.status_code == 200
    with app.app_context():
        b = Borrowing.query.get(bid)
        assert b.status == STATUS_ACTIVE


def test_employee_can_reject(client, employee_user, student_user, sample_book, app):
    _login(client, student_user["email"], student_user["password"])
    client.post("/borrowings/request/" + str(sample_book["id"]), follow_redirects=True)
    with app.app_context():
        bid = Borrowing.query.first().id
    _logout(client)
    _login(client, employee_user["email"], employee_user["password"])
    r = client.post("/borrowings/" + str(bid) + "/reject", data={"reason": "test"}, follow_redirects=True)
    assert r.status_code == 200


def test_employee_can_return(client, employee_user, student_user, sample_book, app):
    _login(client, student_user["email"], student_user["password"])
    client.post("/borrowings/request/" + str(sample_book["id"]), follow_redirects=True)
    with app.app_context():
        bid = Borrowing.query.first().id
    _logout(client)
    _login(client, employee_user["email"], employee_user["password"])
    client.post("/borrowings/" + str(bid) + "/approve", follow_redirects=True)
    r = client.post("/borrowings/" + str(bid) + "/return", follow_redirects=True)
    assert r.status_code == 200
    with app.app_context():
        b = Borrowing.query.get(bid)
        assert b.status == STATUS_RETURNED
        book = Book.query.get(sample_book["id"])
        assert book.available_copies == 3