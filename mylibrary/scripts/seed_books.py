"""Seed sample authors, categories, and books."""
import sys
import os
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.models.book import Author, Book, BookAuthor, Category


AUTHORS = [
    ("حافظ شیرازی", "شاعر بزرگ ایرانی، قرن هشتم", "ایرانی", 1325),
    ("سعدی شیرازی", "شاعر و نویسنده بزرگ ایرانی، قرن هفتم", "ایرانی", 1210),
    ("فردوسی توسی", "سراینده شاهنامه، قرن چهارم", "ایرانی", 940),
    ("مولانا جلال‌الدین", "شاعر و عارف ایرانی، قرن هفتم", "ایرانی", 1207),
    ("نیمایوشیج", "پدر شعر نو فارسی", "ایرانی", 1896),
    ("صادق هدایت", "نویسنده و مترجم ایرانی", "ایرانی", 1903),
    ("سیمین دانشور", "نویسنده و مترجم ایرانی", "ایرانی", 1921),
    ("احمد شاملو", "شاعر و نویسنده ایرانی", "ایرانی", 1925),
]

CATEGORIES = [
    ("شعر کلاسیک", "مجموعه اشعار کلاسیک فارسی"),
    ("رمان فارسی", "رمان‌های نویسندگان ایرانی"),
    ("داستان کوتاه", "مجموعه داستان‌های کوتاه"),
    ("تاریخ ایران", "کتاب‌های تاریخی"),
    ("فلسفه", "کتاب‌های فلسفی"),
    ("علمی", "کتاب‌های علمی و تخصصی"),
]

BOOKS = [
    {"title": "دیوان حافظ", "isbn": "978-600-100-001-1", "author": "حافظ شیرازی", "category": "شعر کلاسیک", "publisher": "امیرکبیر", "publish_year": 1400, "pages": 520, "total_copies": 5, "language": "fa", "description": "مجموعه کامل غزلیات حافظ شیرازی."},
    {"title": "گلستان سعدی", "isbn": "978-600-100-002-8", "author": "سعدی شیرازی", "category": "شعر کلاسیک", "publisher": "خوارزمی", "publish_year": 1399, "pages": 320, "total_copies": 3, "language": "fa", "description": "گلستان سعدی، شاهکار نثر فارسی."},
    {"title": "شاهنامه فردوسی", "isbn": "978-600-100-003-5", "author": "فردوسی توسی", "category": "شعر کلاسیک", "publisher": "توس", "publish_year": 1398, "pages": 1200, "total_copies": 2, "language": "fa", "description": "حماسه ملی ایران."},
    {"title": "مثنوی معنوی", "isbn": "978-600-100-004-2", "author": "مولانا جلال‌الدین", "category": "شعر کلاسیک", "publisher": "علمی", "publish_year": 1397, "pages": 900, "total_copies": 4, "language": "fa", "description": "مثنوی معنوی مولانا."},
    {"title": "بوف کور", "isbn": "978-600-100-005-9", "author": "صادق هدایت", "category": "رمان فارسی", "publisher": "امیرکبیر", "publish_year": 1395, "pages": 180, "total_copies": 6, "language": "fa", "description": "بوف کور، مشهورترین رمان صادق هدایت."},
    {"title": "سووشون", "isbn": "978-600-100-006-6", "author": "سیمین دانشور", "category": "رمان فارسی", "publisher": "خوارزمی", "publish_year": 1396, "pages": 300, "total_copies": 4, "language": "fa", "description": "سووشون، نخستین رمان فارسی یک زن."},
    {"title": "هوای تازه", "isbn": "978-600-100-007-3", "author": "احمد شاملو", "category": "شعر کلاسیک", "publisher": "نگاه", "publish_year": 1394, "pages": 220, "total_copies": 3, "language": "fa", "description": "مجموعه اشعار احمد شاملو."},
    {"title": "افسانه", "isbn": "978-600-100-008-0", "author": "نیمایوشیج", "category": "شعر کلاسیک", "publisher": "نگاه", "publish_year": 1393, "pages": 150, "total_copies": 2, "language": "fa", "description": "افسانه، مجموعه اشعار نیما یوشیج."},
    {"title": "تاریخ ایران باستان", "isbn": "978-600-100-009-7", "author": "فردوسی توسی", "category": "تاریخ ایران", "publisher": "سخن", "publish_year": 1392, "pages": 450, "total_copies": 2, "language": "fa", "description": "تاریخ ایران باستان."},
    {"title": "داستان‌های کوتاه ایرانی", "isbn": "978-600-100-010-3", "author": "صادق هدایت", "category": "داستان کوتاه", "publisher": "امیرکبیر", "publish_year": 1391, "pages": 280, "total_copies": 3, "language": "fa", "description": "مجموعه داستان‌های کوتاه ایرانی."},
]


def main():
    app = create_app("development")
    with app.app_context():
        if db.session.query(Book).count() > 0:
            print(f"Already have {db.session.query(Book).count()} books. Skipping.")
            return

        author_map = {}
        for name, bio, nat, by in AUTHORS:
            a = db.session.query(Author).filter(Author.full_name == name).first()
            if not a:
                a = Author(full_name=name, bio=bio, nationality=nat, birth_year=by)
                db.session.add(a)
                db.session.flush()
            author_map[name] = a
        print(f"OK: {len(author_map)} authors ready")

        cat_map = {}
        for name, desc in CATEGORIES:
            c = db.session.query(Category).filter(Category.name == name).first()
            if not c:
                slug = re.sub(r"[^\w\u0600-\u06FF]+", "-", name.lower()).strip("-")
                c = Category(name=name, slug=slug, description=desc)
                db.session.add(c)
                db.session.flush()
            cat_map[name] = c
        print(f"OK: {len(cat_map)} categories ready")

        for data in BOOKS:
            b = Book(
                title=data["title"], isbn=data["isbn"],
                publisher=data.get("publisher"), publish_year=data.get("publish_year"),
                pages=data.get("pages"),
                total_copies=data.get("total_copies", 1),
                available_copies=data.get("total_copies", 1),
                language=data.get("language", "fa"),
                description=data.get("description"),
                category_id=cat_map[data["category"]].id,
                is_active=True,
            )
            db.session.add(b)
            db.session.flush()
            author = author_map.get(data["author"])
            if author:
                db.session.add(BookAuthor(book_id=b.id, author_id=author.id, position=1))

        db.session.commit()
        print(f"OK: {len(BOOKS)} books created")
        print("\nDONE. Now run: python run.py")


if __name__ == "__main__":
    main()
