"""Library settings model."""
from __future__ import annotations
from app.extensions import db
from app.models.base import BaseModel

class LibrarySettings(BaseModel):
    __tablename__ = "library_settings"
    library_name = db.Column(db.String(150), nullable=False, default="\u06a9\u062a\u0627\u0628\u062e\u0627\u0646\u0647 \u0645\u0631\u06a9\u0632\u06cc \u062f\u0627\u0646\u0634\u06af\u0627\u0647")
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
