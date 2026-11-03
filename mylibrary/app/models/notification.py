"""In-app notification model."""
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
