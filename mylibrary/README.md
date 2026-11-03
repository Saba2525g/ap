# MyLibrary — Smart University Library Management System

A production-grade library management system with Flask, SQLAlchemy, and Persian RTL UI.

![Tests](https://img.shields.io/badge/tests-37%20passed-brightgreen)

## Features

- Book Catalog — search, filter by category/language/availability
- Multi-role Auth — Student, Employee, Admin, Guest
- Borrowing Workflow — request, approve, return with fine
- Reservations — reserve unavailable books
- Notifications — in-app alerts with unread badge
- Dashboard — charts (Chart.js), recent activity, popular books
- Audit Log — track every important action
- Backup/Restore — JSON export/import with validation
- REST API v1 — JWT auth, 20+ endpoints
- Persian RTL UI — Vazirmatn font, navy/gold theme
- Automated Tests — 37 pytest tests, all passing

## Security

- bcrypt password hashing (12 rounds)
- CSRF protection on forms, exempt for API
- JWT (HS256) for API
- Role-based access control
- Rate limiting on auth endpoints
- WTForms validation

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.11+, Flask 3.0+ |
| ORM | SQLAlchemy 2.0 |
| Database | SQLite (dev) / MySQL 8+ (prod) |
| Auth | Flask-Login + Flask-WTF + JWT |
| Frontend | Jinja2, Vanilla JS, Chart.js 4 |
| Tests | pytest, pytest-flask |

## Quick Start (Windows PowerShell)

cd C:\Users\YOUR_USER\Projects\ap\mylibrary
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(48))"
python init_db.py
python scripts/seed_books.py
python scripts/seed_admin.py
python run.py

Open http://127.0.0.1:5000/

## Default Users

| Role | Email |
|------|-------|
| Admin | saba.nouri1385@gmail.com |
| Student | sara.ahmadi44iii@gmail.com |

## Tests

python -m pytest -v
# 37 passed

## API

Full docs: http://127.0.0.1:5000/api/docs

## Author

Saba Nouri — University Software Engineering Project
GitHub: https://github.com/Saba2525g

## License

MIT
