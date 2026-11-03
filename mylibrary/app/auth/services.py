"""Auth services: registration, login, password change."""
from __future__ import annotations

from sqlalchemy import or_

from app.extensions import db
from app.models.user import User, Student, ROLE_STUDENT
from app.models.notification import Notification


class AuthError(Exception):
    """Raised for expected authentication failures."""


def register_student(
    *,
    full_name: str,
    email: str,
    password: str,
    student_number: str,
    phone: str | None = None,
    faculty: str | None = None,
    major: str | None = None,
    enrollment_year: int | None = None,
) -> User:
    """Create a new student account + profile in one transaction."""
    email_norm = email.strip().lower()
    sn_norm = student_number.strip()

    existing = db.session.query(User).filter(or_(User.email == email_norm)).first()
    if existing:
        raise AuthError("این ایمیل قبلاً ثبت شده است.")

    existing_student = db.session.query(Student).filter(Student.student_number == sn_norm).first()
    if existing_student:
        raise AuthError("این شماره دانشجویی قبلاً ثبت شده است.")

    user = User(
        email=email_norm,
        full_name=full_name.strip(),
        role=ROLE_STUDENT,
        phone=phone.strip() if phone else None,
        is_active=True,
    )
    user.set_password(password)

    profile = Student(
        student_number=sn_norm,
        faculty=faculty.strip() if faculty else None,
        major=major.strip() if major else None,
        enrollment_year=enrollment_year,
    )
    user.student = profile

    db.session.add(user)
    db.session.flush()

    db.session.add(Notification(
        user_id=user.id,
        title="خوش آمدید",
        message="حساب کاربری شما با موفقیت ساخته شد. به MyLibrary خوش آمدید.",
        category="success",
        link="/",
    ))

    db.session.commit()
    return user


def authenticate(email: str, password: str) -> User | None:
    """Return the user if credentials are correct, else None."""
    email_norm = (email or "").strip().lower()
    if not email_norm or not password:
        return None
    user = db.session.query(User).filter(User.email == email_norm).first()
    if not user or not user.is_active:
        return None
    if not user.check_password(password):
        return None
    user.touch_login()
    db.session.commit()
    return user


def change_password(user: User, current: str, new: str) -> None:
    if not user.check_password(current):
        raise AuthError("رمز فعلی اشتباه است.")
    if current == new:
        raise AuthError("رمز جدید باید با رمز قبلی متفاوت باشد.")
    user.set_password(new)
    db.session.commit()


def update_profile(user: User, *, full_name: str, phone: str | None) -> None:
    user.full_name = full_name.strip()
    user.phone = phone.strip() if phone else None
    db.session.commit()