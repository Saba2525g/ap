"""Exempt /api/* blueprints from CSRF (they use JWT instead)."""
from app.extensions import csrf
from app.api.auth import bp as auth_bp
from app.api.books import bp as books_bp
from app.api.borrowings import bp as borrowings_bp
from app.api.users import bp as users_bp
from app.api.stats import bp as stats_bp

API_BLUEPRINTS = [auth_bp, books_bp, borrowings_bp, users_bp, stats_bp]


def register_api_csrf_exemption():
    for bp in API_BLUEPRINTS:
        csrf.exempt(bp)