"""REST API v1."""
from app.api.auth import bp as auth_bp
from app.api.books import bp as books_bp
from app.api.borrowings import bp as borrowings_bp
from app.api.users import bp as users_bp
from app.api.stats import bp as stats_bp

__all__ = ["auth_bp", "books_bp", "borrowings_bp", "users_bp", "stats_bp"]
