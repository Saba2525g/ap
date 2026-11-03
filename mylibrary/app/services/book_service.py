"""Book service: CRUD + search."""
from __future__ import annotations

import re

from sqlalchemy import func, or_

from app.extensions import db
from app.models.book import Author, Book, BookAuthor, Category


class BookError(Exception):
    """Raised for expected book errors."""


def _slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\u0600-\u06FF]+", "-", text, flags=re.UNICODE)
    return text.strip("-") or "cat"


def list_categories():
    return db.session.query(Category).order_by(Category.name).all()


def list_authors():
    return db.session.query(Author).order_by(Author.full_name).all()


def search_books(*, q=None, category_id=None, language=None, available_only=False,
                 include_inactive=False, limit=50, offset=0):
    query = db.session.query(Book)
    if not include_inactive:
        query = query.filter(Book.is_active.is_(True))
    if q:
        like = f"%{q.strip()}%"
        query = query.outerjoin(BookAuthor).outerjoin(Author).filter(
            or_(Book.title.ilike(like), Book.isbn.ilike(like),
                Book.publisher.ilike(like), Author.full_name.ilike(like))
        ).distinct()
    if category_id:
        query = query.filter(Book.category_id == category_id)
    if language:
        query = query.filter(Book.language == language)
    if available_only:
        query = query.filter(Book.available_copies > 0)
    total = query.count()
    items = query.order_by(Book.title).offset(offset).limit(limit).all()
    return items, total


def get_book(book_id):
    return db.session.get(Book, book_id)


def create_book(*, title, isbn, total_copies=1, author_ids=None, category_id=None,
                description=None, publisher=None, publish_year=None, language="fa",
                pages=None, shelf_location=None, cover_url=None):
    isbn = isbn.strip()
    if not title.strip():
        raise BookError("عنوان الزامی است.")
    if db.session.query(Book).filter(Book.isbn == isbn).first():
        raise BookError("این ISBN قبلاً ثبت شده است.")
    if total_copies < 0:
        raise BookError("تعداد نسخه نمی‌تواند منفی باشد.")
    book = Book(title=title.strip(), isbn=isbn, total_copies=total_copies,
                available_copies=total_copies, category_id=category_id,
                description=description, publisher=publisher, publish_year=publish_year,
                language=language or "fa", pages=pages, shelf_location=shelf_location,
                cover_url=cover_url, is_active=True)
    db.session.add(book)
    db.session.flush()
    for pos, aid in enumerate(author_ids or [], start=1):
        if db.session.get(Author, aid):
            db.session.add(BookAuthor(book_id=book.id, author_id=aid, position=pos))
    db.session.commit()
    return book


def update_book(book, **fields):
    author_ids = fields.pop("author_ids", None)
    for k, v in fields.items():
        setattr(book, k, v)
    if author_ids is not None:
        db.session.query(BookAuthor).filter(BookAuthor.book_id == book.id).delete()
        for pos, aid in enumerate(author_ids, start=1):
            if db.session.get(Author, aid):
                db.session.add(BookAuthor(book_id=book.id, author_id=aid, position=pos))
    db.session.commit()
    return book


def delete_book(book):
    if book.borrowings.count() > 0:
        book.is_active = False
        db.session.commit()
        return
    db.session.delete(book)
    db.session.commit()


def create_category(name, description=None):
    name = name.strip()
    if not name:
        raise BookError("نام دسته الزامی است.")
    if db.session.query(Category).filter(Category.name == name).first():
        raise BookError("این دسته قبلاً وجود دارد.")
    slug = _slugify(name)
    base = slug
    i = 1
    while db.session.query(Category).filter(Category.slug == slug).first():
        i += 1
        slug = f"{base}-{i}"
    cat = Category(name=name, slug=slug, description=description)
    db.session.add(cat)
    db.session.commit()
    return cat


def create_author(full_name, bio=None, nationality=None, birth_year=None):
    full_name = full_name.strip()
    if not full_name:
        raise BookError("نام نویسنده الزامی است.")
    a = Author(full_name=full_name, bio=bio, nationality=nationality, birth_year=birth_year)
    db.session.add(a)
    db.session.commit()
    return a


def stats():
    return {
        "total_books": db.session.query(func.count(Book.id)).scalar() or 0,
        "available_books": db.session.query(func.count(Book.id)).filter(Book.available_copies > 0).scalar() or 0,
        "total_categories": db.session.query(func.count(Category.id)).scalar() or 0,
        "total_authors": db.session.query(func.count(Author.id)).scalar() or 0,
    }
