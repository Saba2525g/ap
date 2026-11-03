"""Borrowing & Reservation models."""
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
