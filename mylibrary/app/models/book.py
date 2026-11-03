"""Book, Author, Category, BookAuthor models."""
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
        return ", ".join(names) if names else "\u2014"

    def __repr__(self) -> str:
        return f"<Book {self.title!r} ({self.isbn})>"

class BookAuthor(db.Model):
    __tablename__ = "book_authors"
    book_id = db.Column(db.Integer, db.ForeignKey("books.id", ondelete="CASCADE"), primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True)
    position = db.Column(db.Integer, nullable=False, default=1)
    book = db.relationship("Book", back_populates="author_links")
    author = db.relationship("Author", back_populates="book_links")
