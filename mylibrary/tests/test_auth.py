"""Tests for authentication and authorization."""
from app.models.user import User


def test_home_page(client):
    r = client.get("/")
    assert r.status_code == 200


def test_login_page_loads(client):
    r = client.get("/auth/login")
    assert r.status_code == 200
    assert "ورود".encode() in r.data


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
        "email": student_user["email"],
        "password": student_user["password"],
    }, follow_redirects=True)
    assert r.status_code == 200
    assert "خوش آمدید".encode() in r.data


def test_login_wrong_password(client, student_user):
    r = client.post("/auth/login", data={
        "email": student_user["email"],
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
    client.post("/auth/login", data={"email": student_user["email"], "password": student_user["password"]})
    r = client.get("/borrowings/requests", follow_redirects=False)
    assert r.status_code == 403


def test_admin_can_access_audit(client, admin_user):
    client.post("/auth/login", data={"email": admin_user["email"], "password": admin_user["password"]})
    r = client.get("/admin/audit")
    assert r.status_code == 200
