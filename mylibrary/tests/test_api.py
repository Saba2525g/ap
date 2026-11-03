"""Tests for REST API."""


def test_api_login_success(client, admin_user):
    r = client.post("/api/v1/auth/login", json={
        "email": admin_user["email"], "password": admin_user["password"]})
    assert r.status_code == 200
    data = r.get_json()
    assert "access_token" in data
    assert data["user"]["email"] == "admin@test.com"


def test_api_login_fail(client, admin_user):
    r = client.post("/api/v1/auth/login", json={
        "email": admin_user["email"], "password": "wrong"})
    assert r.status_code == 401


def test_api_me_requires_token(client):
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 401


def test_api_me_success(client, admin_user):
    r = client.post("/api/v1/auth/login", json={
        "email": admin_user["email"], "password": admin_user["password"]})
    token = r.get_json()["access_token"]
    r2 = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    assert r2.get_json()["user"]["email"] == admin_user["email"]


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
    r = client.post("/api/v1/auth/login", json={
        "email": admin_user["email"], "password": admin_user["password"]})
    token = r.get_json()["access_token"]
    r2 = client.post("/api/v1/books",
                     json={"title": "API Book", "isbn": "API-1", "total_copies": 2},
                     headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 201
    assert r2.get_json()["isbn"] == "API-1"


def test_api_student_cannot_create_book(client, student_user):
    r = client.post("/api/v1/auth/login", json={
        "email": student_user["email"], "password": student_user["password"]})
    token = r.get_json()["access_token"]
    r2 = client.post("/api/v1/books", json={"title": "X", "isbn": "Y"},
                     headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 403
