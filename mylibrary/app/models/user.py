"""User / Student / Employee models."""
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

    student = db.relationship("Student", back_populates="user", uselist=False,
                              cascade="all, delete-orphan")
    employee = db.relationship("Employee", back_populates="user", uselist=False,
                               cascade="all, delete-orphan")
    notifications = db.relationship("Notification", back_populates="user",
                                    cascade="all, delete-orphan", lazy="dynamic")
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

    def touch_login(self) -> None:
        self.last_login_at = datetime.now(timezone.utc)

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"


class Student(BaseModel, TimestampMixin):
    __tablename__ = "students"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"),
                        unique=True, nullable=False)
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

    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"),
                        unique=True, nullable=False)
    employee_number = db.Column(db.String(30), unique=True, nullable=False, index=True)
    department = db.Column(db.String(120), nullable=True)
    position = db.Column(db.String(120), nullable=True)
    hire_date = db.Column(db.Date, nullable=True)

    user = db.relationship("User", back_populates="employee")

    def __repr__(self) -> str:
        return f"<Employee {self.employee_number}>"