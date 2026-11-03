"""Borrowing, return, and reservation business logic."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.extensions import db
from app.models.book import Book
from app.models.borrowing import (
    Borrowing, Reservation,
    STATUS_PENDING, STATUS_APPROVED, STATUS_REJECTED, STATUS_ACTIVE,
    STATUS_RETURNED, STATUS_OVERDUE, STATUS_CANCELLED,
    RES_PENDING, RES_READY, RES_FULFILLED, RES_CANCELLED, RES_EXPIRED,
)
from app.models.notification import Notification
from app.models.settings import LibrarySettings


class BorrowError(Exception):
    """Raised for expected borrowing errors."""


def _utcnow():
    return datetime.now(timezone.utc)


def _notify(user_id, title, message, category="info", link=None):
    db.session.add(Notification(
        user_id=user_id, title=title, message=message,
        category=category, link=link,
    ))


def request_borrow(student, book, *, notes=None):
    """Create a pending borrowing request."""
    if not book.is_active:
        raise BorrowError("این کتاب غیرفعال است.")
    if book.available_copies <= 0:
        raise BorrowError("این کتاب موجود نیست. از رزرو استفاده کنید.")

    settings = LibrarySettings.get_current()
    active_count = db.session.query(Borrowing).filter(
        Borrowing.student_id == student.id,
        Borrowing.status.in_([STATUS_PENDING, STATUS_APPROVED, STATUS_ACTIVE, STATUS_OVERDUE]),
    ).count()
    if active_count >= settings.max_active_loans_per_student:
        raise BorrowError(f"حداکثر {settings.max_active_loans_per_student} امانت فعال مجاز است.")

    existing = db.session.query(Borrowing).filter(
        Borrowing.student_id == student.id,
        Borrowing.book_id == book.id,
        Borrowing.status.in_([STATUS_PENDING, STATUS_APPROVED, STATUS_ACTIVE, STATUS_OVERDUE]),
    ).first()
    if existing:
        raise BorrowError("شما قبلاً برای این کتاب درخواست فعال دارید.")

    b = Borrowing(
        student_id=student.id, book_id=book.id,
        status=STATUS_PENDING, requested_at=_utcnow(),
    )
    db.session.add(b)
    db.session.flush()
    _notify(student.user_id, "درخواست امانت ثبت شد",
            f"درخواست شما برای «{book.title}» ثبت شد. منتظر تأیید باشید.",
            "info", "/borrowings/my")
    db.session.commit()
    return b


def approve_borrow(borrowing, employee_user):
    """Approve a pending request and check out the book."""
    if borrowing.status != STATUS_PENDING:
        raise BorrowError("این درخواست در وضعیت قابل تأیید نیست.")
    book = borrowing.book
    if book.available_copies <= 0:
        raise BorrowError("نسخه‌ای موجود نیست.")

    settings = LibrarySettings.get_current()
    now = _utcnow()
    borrowing.status = STATUS_APPROVED
    borrowing.approved_at = now
    borrowing.approved_by_id = employee_user.id
    borrowing.checked_out_at = now
    borrowing.due_date = now + timedelta(days=settings.loan_days)
    borrowing.status = STATUS_ACTIVE
    book.available_copies -= 1

    _notify(borrowing.student.user_id, "امانت تأیید شد",
            f"کتاب «{book.title}» تا {settings.loan_days} روز آینده باید بازگردانده شود.",
            "success", "/borrowings/my")
    db.session.commit()


def reject_borrow(borrowing, employee_user, reason=""):
    if borrowing.status != STATUS_PENDING:
        raise BorrowError("این درخواست در وضعیت قابل رد نیست.")
    borrowing.status = STATUS_REJECTED
    borrowing.rejected_at = _utcnow()
    borrowing.approved_by_id = employee_user.id
    borrowing.rejection_reason = reason or "بدون دلیل"
    _notify(borrowing.student.user_id, "درخواست امانت رد شد",
            f"درخواست «{borrowing.book.title}» رد شد. دلیل: {reason or 'نامشخص'}",
            "danger", "/borrowings/my")
    db.session.commit()


def return_book(borrowing, employee_user=None):
    """Mark a book as returned, compute fine."""
    if borrowing.status not in (STATUS_ACTIVE, STATUS_OVERDUE):
        raise BorrowError("این امانت در وضعیت قابل بازگشت نیست.")
    settings = LibrarySettings.get_current()
    now = _utcnow()
    borrowing.returned_at = now
    fine = borrowing.compute_fine(settings.fine_per_day)
    borrowing.fine_amount = fine
    borrowing.status = STATUS_RETURNED

    book = borrowing.book
    book.available_copies = min(book.available_copies + 1, book.total_copies)

    msg = f"کتاب «{book.title}» بازگردانده شد."
    if fine > 0:
        msg += f" جریمه: {fine:,} ریال"
    _notify(borrowing.student.user_id, "بازگشت کتاب ثبت شد", msg,
            "warning" if fine > 0 else "success", "/borrowings/my")
    db.session.commit()


def reserve_book(student, book):
    """Create a reservation for an unavailable book."""
    if book.available_copies > 0:
        raise BorrowError("این کتاب موجود است — می‌توانید درخواست امانت بدهید.")

    existing = db.session.query(Reservation).filter(
        Reservation.student_id == student.id,
        Reservation.book_id == book.id,
        Reservation.status.in_([RES_PENDING, RES_READY]),
    ).first()
    if existing:
        raise BorrowError("شما قبلاً این کتاب را رزرو کرده‌اید.")

    settings = LibrarySettings.get_current()
    r = Reservation(
        student_id=student.id, book_id=book.id,
        status=RES_PENDING, reserved_at=_utcnow(),
        expires_at=_utcnow() + timedelta(days=settings.reservation_hold_days),
    )
    db.session.add(r)
    _notify(student.user_id, "رزرو ثبت شد",
            f"کتاب «{book.title}» رزرو شد. در صورت موجود شدن اطلاع می‌دهیم.",
            "info", "/borrowings/my")
    db.session.commit()
    return r


def cancel_reservation(reservation):
    if not reservation.is_active:
        raise BorrowError("این رزرو فعال نیست.")
    reservation.status = RES_CANCELLED
    reservation.cancelled_at = _utcnow()
    db.session.commit()


def mark_overdue():
    """Sweep: mark active loans past due as overdue."""
    now = _utcnow()
    q = db.session.query(Borrowing).filter(
        Borrowing.status == STATUS_ACTIVE,
        Borrowing.due_date < now,
    )
    count = 0
    for b in q.all():
        b.status = STATUS_OVERDUE
        count += 1
    db.session.commit()
    return count


def stats():
    return {
        "pending": db.session.query(Borrowing).filter(Borrowing.status == STATUS_PENDING).count(),
        "active": db.session.query(Borrowing).filter(Borrowing.status.in_([STATUS_ACTIVE, STATUS_OVERDUE])).count(),
        "overdue": db.session.query(Borrowing).filter(Borrowing.status == STATUS_OVERDUE).count(),
        "returned": db.session.query(Borrowing).filter(Borrowing.status == STATUS_RETURNED).count(),
    }
