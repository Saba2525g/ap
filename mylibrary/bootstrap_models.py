"""One-time script to write all model files. Run from mylibrary/ root."""
import os

FILES = {}

FILES["app/utils/__init__.py"] = '"""Utility helpers."""\n'

FILES["app/utils/security.py"] = '''"""Password hashing & verification helpers (bcrypt)."""
from __future__ import annotations
import bcrypt

BCRYPT_ROUNDS = 12
MAX_PASSWORD_BYTES = 72

def hash_password(plain: str) -> str:
    if not plain:
        raise ValueError("password must not be empty")
    raw = plain.encode("utf-8")
    if len(raw) > MAX_PASSWORD_BYTES:
        raw = raw[:MAX_PASSWORD_BYTES]
    return bcrypt.hashpw(raw, bcrypt.gensalt(rounds=BCRYPT_ROUNDS)).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    if not plain or not hashed:
        return False
    try:
        raw = plain.encode("utf-8")[:MAX_PASSWORD_BYTES]
        return bcrypt.checkpw(raw, hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False
'''

FILES["app/utils/datetime.py"] = '''"""Date/time helpers with Jalali (Persian) calendar support."""
from __future__ import annotations
from datetime import datetime, timezone, date

def gregorian_to_jalali(gy: int, gm: int, gd: int):
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if gy > 1600:
        jy = 979
        gy -= 1600
    else:
        jy = 0
        gy -= 621
    gy2 = gy + 1 if gm > 2 else gy
    days = (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + ((gy2 + 399) // 400) - 80 + gd + g_d_m[gm - 1]
    jy += 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm = 1 + (days // 31)
        jd = 1 + (days % 31)
    else:
        jm = 7 + ((days - 186) // 30)
        jd = 1 + ((days - 186) % 30)
    return jy, jm, jd

def jalali_to_gregorian(jy: int, jm: int, jd: int):
    if jy > 979:
        gy = 1600
        jy -= 979
    else:
        gy = 621
    days = (365 * jy) + ((jy // 33) * 8) + (((jy % 33) + 3) // 4) + 78 + jd + (
        (jm - 1) * 31 if jm < 7 else ((jm - 7) * 30) + 186
    )
    gy += 400 * (days // 146097)
    days %= 146097
    if days > 36524:
        days -= 1
        gy += 100 * (days // 36524)
        days %= 36524
        if days >= 365:
            days += 1
    gy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        gy += (days - 1) // 365
        days = (days - 1) % 365
    gd = days + 1
    sal_a = [0, 31, 29 if (gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0) else 28,
             31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    gm = 1
    for i in range(1, 13):
        if gd <= sal_a[i]:
            gm = i
            break
        gd -= sal_a[i]
    return gy, gm, gd

PERSIAN_MONTHS = ["\\u0641\\u0631\\u0648\\u0631\\u062f\\u06cc\\u0646", "\\u0627\\u0631\\u062f\\u06cc\\u0628\\u0647\\u0634\\u062a", "\\u062e\\u0631\\u062f\\u0627\\u062f", "\\u062a\\u06cc\\u0631", "\\u0645\\u0631\\u062f\\u0627\\u062f", "\\u0634\\u0647\\u0631\\u06cc\\u0648\\u0631",
                  "\\u0645\\u0647\\u0631", "\\u0622\\u0628\\u0627\\u0646", "\\u0622\\u0630\\u0631", "\\u062f\\u06cc", "\\u0628\\u0647\\u0645\\u0646", "\\u0627\\u0633\\u0641\\u0646\\u062f"]

def to_jalali_string(dt, with_time: bool = False) -> str:
    if dt is None:
        return "\\u2014"
    if isinstance(dt, datetime):
        jy, jm, jd = gregorian_to_jalali(dt.year, dt.month, dt.day)
        out = f"{jd} {PERSIAN_MONTHS[jm - 1]} {jy}"
        if with_time:
            out += f" - {dt.hour:02d}:{dt.minute:02d}"
        return out
    if isinstance(dt, date):
        jy, jm, jd = gregorian_to_jalali(dt.year, dt.month, dt.day)
        return f"{jd} {PERSIAN_MONTHS[jm - 1]} {jy}"
    return str(dt)

def to_persian_digits(value) -> str:
    mapping = str.maketrans("0123456789", "\\u06f0\\u06f1\\u06f2\\u06f3\\u06f4\\u06f5\\u06f6\\u06f7\\u06f8\\u06f9")
    return str(value).translate(mapping)

def utcnow() -> datetime:
    return datetime.now(timezone.utc)
'''

FILES["app/models/base.py"] = '''"""Base model mixin with common columns."""
from __future__ import annotations
from datetime import datetime, timezone
from app.extensions import db

def _utcnow():
    return datetime.now(timezone.utc)

class TimestampMixin:
    created_at = db.Column(db.DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False)

class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False)
'''

FILES["app/models/user.py"] = '''"""User / Student / Employee models."""
from __future__ import annotations
from datetime import datetime, timezone
from flask_login import UserMixin
from app.extensions import db
from app.models.base import BaseModel, TimestampMixin
from app.utils.security import hash_password, verify_password

ROLE_STUDENT = "student"
ROLE_EMPLOYEE = "employee"
ROLE_ADMIN = "admin"
ROLE_GUEST = "guest"
VALID_ROLES = {ROLE_STUDENT, ROLE_EMPLOYEE, ROLE_ADMIN, ROLE_GUEST}

class User(BaseModel, UserMixin):
    __tablename__ = "users"
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=ROLE_STUDENT, index=True)
    phone = db.Column(db.String(20), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    last_login_at = db.Column(db.DateTime(timezone=True), nullable=True)
    student = db.relationship("Student", back_populates="user", uselist=False, cascade="all, delete-orphan")
    employee = db.relationship("Employee", back_populates="user", uselist=False, cascade="all, delete-orphan")
    notifications = db.relationship("Notification", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    audit_logs = db.relationship("AuditLog", back_populates="actor", lazy="dynamic")

    def set_password(self, plain: str) -> None:
        self.password_hash = hash_password(plain)

    def check_password(self, plain: str) -> bool:
        return verify_password(plain, self.password_hash)

    @property
    def is_student(self) -> bool:
        return self.role == ROLE_STUDENT

    @property
    def is_employee(self) -> bool:
        return self.role == ROLE_EMPLOYEE

    @property
    def is_admin(self) -> bool:
        return self.role == ROLE_ADMIN

    @property
    def can_manage_books(self) -> bool:
        return self.role in (ROLE_EMPLOYEE, ROLE_ADMIN)

    @property
    def is_active(self):  # type: ignore[override]
        return bool(self.is_active)

    def touch_login(self) -> None:
        self.last_login_at = datetime.now(timezone.utc)

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"

class Student(BaseModel, TimestampMixin):
    __tablename__ = "students"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    student_number = db.Column(db.String(30), unique=True, nullable=False, index=True)
    faculty = db.Column(db.String(120), nullable=True)
    major = db.Column(db.String(120), nullable=True)
    enrollment_year = db.Column(db.Integer, nullable=True)
    user = db.relationship("User", back_populates="student")
    borrowings = db.relationship("Borrowing", back_populates="student", lazy="dynamic")
    reservations = db.relationship("Reservation", back_populates="student", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Student {self.student_number}>"

class Employee(BaseModel, TimestampMixin):
    __tablename__ = "employees"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    employee_number = db.Column(db.String(30), unique=True, nullable=False, index=True)
    department = db.Column(db.String(120), nullable=True)
    position = db.Column(db.String(120), nullable=True)
    hire_date = db.Column(db.Date, nullable=True)
    user = db.relationship("User", back_populates="employee")

    def __repr__(self) -> str:
        return f"<Employee {self.employee_number}>"
'''

FILES["app/models/book.py"] = '''"""Book, Author, Category, BookAuthor models."""
from __future__ import annotations
from app.extensions import db
from app.models.base import BaseModel, TimestampMixin

class Category(BaseModel, TimestampMixin):
    __tablename__ = "categories"
    name = db.Column(db.String(120), unique=True, nullable=False, index=True)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    books = db.relationship("Book", back_populates="category", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Category {self.name}>"

class Author(BaseModel, TimestampMixin):
    __tablename__ = "authors"
    full_name = db.Column(db.String(180), nullable=False, index=True)
    bio = db.Column(db.Text, nullable=True)
    nationality = db.Column(db.String(80), nullable=True)
    birth_year = db.Column(db.Integer, nullable=True)
    book_links = db.relationship("BookAuthor", back_populates="author", cascade="all, delete-orphan", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Author {self.full_name}>"

class Book(BaseModel, TimestampMixin):
    __tablename__ = "books"
    title = db.Column(db.String(255), nullable=False, index=True)
    isbn = db.Column(db.String(20), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    publisher = db.Column(db.String(150), nullable=True)
    publish_year = db.Column(db.Integer, nullable=True)
    language = db.Column(db.String(10), nullable=False, default="fa")
    pages = db.Column(db.Integer, nullable=True)
    cover_url = db.Column(db.String(500), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    total_copies = db.Column(db.Integer, nullable=False, default=1)
    available_copies = db.Column(db.Integer, nullable=False, default=1)
    shelf_location = db.Column(db.String(60), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    category = db.relationship("Category", back_populates="books")
    author_links = db.relationship("BookAuthor", back_populates="book", cascade="all, delete-orphan", lazy="selectin")
    borrowings = db.relationship("Borrowing", back_populates="book", lazy="dynamic")
    reservations = db.relationship("Reservation", back_populates="book", lazy="dynamic")
    __table_args__ = (
        db.CheckConstraint("total_copies >= 0", name="ck_book_total_non_negative"),
        db.CheckConstraint("available_copies >= 0", name="ck_book_available_non_negative"),
        db.CheckConstraint("available_copies <= total_copies", name="ck_book_available_le_total"),
    )

    @property
    def is_available(self) -> bool:
        return self.is_active and self.available_copies > 0

    @property
    def author_names(self) -> str:
        names = [link.author.full_name for link in self.author_links if link.author]
        return ", ".join(names) if names else "\\u2014"

    def __repr__(self) -> str:
        return f"<Book {self.title!r} ({self.isbn})>"

class BookAuthor(db.Model):
    __tablename__ = "book_authors"
    book_id = db.Column(db.Integer, db.ForeignKey("books.id", ondelete="CASCADE"), primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True)
    position = db.Column(db.Integer, nullable=False, default=1)
    book = db.relationship("Book", back_populates="author_links")
    author = db.relationship("Author", back_populates="book_links")
'''

FILES["app/models/borrowing.py"] = '''"""Borrowing & Reservation models."""
from __future__ import annotations
from datetime import datetime, timezone
from app.extensions import db
from app.models.base import BaseModel, TimestampMixin

STATUS_PENDING = "pending"
STATUS_APPROVED = "approved"
STATUS_REJECTED = "rejected"
STATUS_ACTIVE = "active"
STATUS_RETURNED = "returned"
STATUS_OVERDUE = "overdue"
STATUS_CANCELLED = "cancelled"
BORROW_STATUSES = {STATUS_PENDING, STATUS_APPROVED, STATUS_REJECTED, STATUS_ACTIVE, STATUS_RETURNED, STATUS_OVERDUE, STATUS_CANCELLED}
RES_PENDING = "pending"
RES_READY = "ready"
RES_FULFILLED = "fulfilled"
RES_CANCELLED = "cancelled"
RES_EXPIRED = "expired"
RESERVATION_STATUSES = {RES_PENDING, RES_READY, RES_FULFILLED, RES_CANCELLED, RES_EXPIRED}

class Borrowing(BaseModel, TimestampMixin):
    __tablename__ = "borrowings"
    student_id = db.Column(db.Integer, db.ForeignKey("students.id", ondelete="RESTRICT"), nullable=False, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id", ondelete="RESTRICT"), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default=STATUS_PENDING, index=True)
    requested_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    approved_at = db.Column(db.DateTime(timezone=True), nullable=True)
    approved_by_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    rejected_at = db.Column(db.DateTime(timezone=True), nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    checked_out_at = db.Column(db.DateTime(timezone=True), nullable=True)
    due_date = db.Column(db.DateTime(timezone=True), nullable=True, index=True)
    returned_at = db.Column(db.DateTime(timezone=True), nullable=True)
    fine_amount = db.Column(db.Integer, nullable=False, default=0)
    fine_paid = db.Column(db.Boolean, nullable=False, default=False)
    student = db.relationship("Student", back_populates="borrowings")
    book = db.relationship("Book", back_populates="borrowings")
    approved_by = db.relationship("User", foreign_keys=[approved_by_id])

    @property
    def is_overdue(self) -> bool:
        if self.status in (STATUS_RETURNED, STATUS_REJECTED, STATUS_CANCELLED):
            return False
        if not self.due_date:
            return False
        return datetime.now(timezone.utc) > self.due_date

    def compute_fine(self, fine_per_day: int) -> int:
        if not self.due_date or not self.returned_at:
            return self.fine_amount or 0
        if self.returned_at <= self.due_date:
            return 0
        days_late = (self.returned_at - self.due_date).days
        return max(0, days_late) * fine_per_day

    def __repr__(self) -> str:
        return f"<Borrowing #{self.id} student={self.student_id} book={self.book_id} status={self.status}>"

class Reservation(BaseModel, TimestampMixin):
    __tablename__ = "reservations"
    student_id = db.Column(db.Integer, db.ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default=RES_PENDING, index=True)
    reserved_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    ready_at = db.Column(db.DateTime(timezone=True), nullable=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=True, index=True)
    fulfilled_at = db.Column(db.DateTime(timezone=True), nullable=True)
    cancelled_at = db.Column(db.DateTime(timezone=True), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    student = db.relationship("Student", back_populates="reservations")
    book = db.relationship("Book", back_populates="reservations")

    @property
    def is_active(self) -> bool:
        return self.status in (RES_PENDING, RES_READY)

    def __repr__(self) -> str:
        return f"<Reservation #{self.id} student={self.student_id} book={self.book_id} status={self.status}>"
'''

FILES["app/models/notification.py"] = '''"""In-app notification model."""
from __future__ import annotations
from datetime import datetime, timezone
from app.extensions import db
from app.models.base import BaseModel

class Notification(BaseModel):
    __tablename__ = "notifications"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(30), nullable=False, default="info")
    link = db.Column(db.String(500), nullable=True)
    is_read = db.Column(db.Boolean, nullable=False, default=False, index=True)
    read_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    user = db.relationship("User", back_populates="notifications")

    def mark_read(self) -> None:
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.now(timezone.utc)

    def __repr__(self) -> str:
        return f"<Notification #{self.id} user={self.user_id}>"
'''

FILES["app/models/audit_log.py"] = '''"""Audit log."""
from __future__ import annotations
from datetime import datetime, timezone
from app.extensions import db
from app.models.base import BaseModel

class AuditLog(BaseModel):
    __tablename__ = "audit_logs"
    actor_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = db.Column(db.String(100), nullable=False, index=True)
    entity_type = db.Column(db.String(60), nullable=True, index=True)
    entity_id = db.Column(db.Integer, nullable=True, index=True)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    actor = db.relationship("User", back_populates="audit_logs")

    def __repr__(self) -> str:
        return f"<AuditLog {self.action} by={self.actor_id}>"
'''

FILES["app/models/settings.py"] = '''"""Library settings model."""
from __future__ import annotations
from app.extensions import db
from app.models.base import BaseModel

class LibrarySettings(BaseModel):
    __tablename__ = "library_settings"
    library_name = db.Column(db.String(150), nullable=False, default="\\u06a9\\u062a\\u0627\\u0628\\u062e\\u0627\\u0646\\u0647 \\u0645\\u0631\\u06a9\\u0632\\u06cc \\u062f\\u0627\\u0646\\u0634\\u06af\\u0627\\u0647")
    address = db.Column(db.String(300), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    loan_days = db.Column(db.Integer, nullable=False, default=14)
    max_active_loans_per_student = db.Column(db.Integer, nullable=False, default=5)
    fine_per_day = db.Column(db.Integer, nullable=False, default=5000)
    reservation_hold_days = db.Column(db.Integer, nullable=False, default=3)
    updated_by_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    @classmethod
    def get_current(cls):
        s = cls.query.first()
        if s is None:
            s = cls()
            db.session.add(s)
            db.session.commit()
        return s

    def __repr__(self) -> str:
        return f"<LibrarySettings #{self.id} loan_days={self.loan_days}>"
'''

FILES["app/models/__init__.py"] = '''"""SQLAlchemy models. Import all here for Alembic discovery."""
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
'''

for path, content in FILES.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"WROTE {path} ({len(content)} bytes)")

print("\nDONE: all model files written.")
