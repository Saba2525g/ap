"""SQLAlchemy models. Import all here for Alembic discovery."""
from app.models.base import BaseModel, TimestampMixin
from app.models.user import User, Student, Employee, ROLE_STUDENT, ROLE_EMPLOYEE, ROLE_ADMIN, ROLE_GUEST, VALID_ROLES
from app.models.book import Book, Author, Category, BookAuthor
from app.models.borrowing import (
    Borrowing, Reservation,
    STATUS_PENDING, STATUS_APPROVED, STATUS_REJECTED,
    STATUS_ACTIVE, STATUS_RETURNED, STATUS_OVERDUE, STATUS_CANCELLED,
    BORROW_STATUSES,
    RES_PENDING, RES_READY, RES_FULFILLED, RES_CANCELLED, RES_EXPIRED,
    RESERVATION_STATUSES,
)
from app.models.notification import Notification
from app.models.audit_log import AuditLog
from app.models.settings import LibrarySettings

__all__ = [
    "BaseModel", "TimestampMixin",
    "User", "Student", "Employee",
    "ROLE_STUDENT", "ROLE_EMPLOYEE", "ROLE_ADMIN", "ROLE_GUEST", "VALID_ROLES",
    "Book", "Author", "Category", "BookAuthor",
    "Borrowing", "Reservation",
    "STATUS_PENDING", "STATUS_APPROVED", "STATUS_REJECTED",
    "STATUS_ACTIVE", "STATUS_RETURNED", "STATUS_OVERDUE", "STATUS_CANCELLED",
    "BORROW_STATUSES",
    "RES_PENDING", "RES_READY", "RES_FULFILLED", "RES_CANCELLED", "RES_EXPIRED",
    "RESERVATION_STATUSES",
    "Notification", "AuditLog", "LibrarySettings",
]
