"""Books API endpoints."""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.api._helpers import _error, api_auth_required
from app.services import book_service as svc

bp = Blueprint("api_books", __name__, url_prefix="/api/v1/books")


def _book_json(b) -> dict:
    return {
        "id": b.id,
        "title": b.title,
        "isbn": b.isbn,
        "publisher": b.publisher,
        "publish_year": b.publish_year,
        "language": b.language,
        "pages": b.pages,
        "cover_url": b.cover_url,
        "description": b.description,
        "category": ({"id": b.category.id, "name": b.category.name} if b.category else None),
        "authors": [{"id": l.author.id, "name": l.author.full_name} for l in b.author_links if l.author],
        "total_copies": b.total_copies,
        "available_copies": b.available_copies,
        "is_available": b.is_available,
        "is_active": b.is_active,
    }


@bp.route("", methods=["GET"])
@bp.route("/", methods=["GET"])
def list_books():
    q = request.args.get("q")
    cat = request.args.get("category", type=int)
    lang = request.args.get("language")
    avail = request.args.get("available") == "1"
    page = max(1, request.args.get("page", 1, type=int))
    per_page = min(100, request.args.get("per_page", 20, type=int))
    items, total = svc.search_books(
        q=q, category_id=cat, language=lang,
        available_only=avail, limit=per_page, offset=(page - 1) * per_page,
    )
    return jsonify({
        "items": [_book_json(b) for b in items],
        "total": total, "page": page, "per_page": per_page,
        "pages": max(1, (total + per_page - 1) // per_page),
    })


@bp.route("/<int:bid>", methods=["GET"])
def get_book(bid):
    b = svc.get_book(bid)
    if not b:
        return _error("book not found", 404, "not_found")
    return jsonify(_book_json(b))


@bp.route("", methods=["POST"])
@bp.route("/", methods=["POST"])
@api_auth_required("employee", "admin")
def create_book():
    data = request.get_json(silent=True) or {}
    try:
        book = svc.create_book(
            title=data.get("title", ""),
            isbn=data.get("isbn", ""),
            total_copies=int(data.get("total_copies", 1)),
            author_ids=data.get("author_ids") or [],
            category_id=data.get("category_id"),
            description=data.get("description"),
            publisher=data.get("publisher"),
            publish_year=data.get("publish_year"),
            language=data.get("language", "fa"),
            pages=data.get("pages"),
            shelf_location=data.get("shelf_location"),
            cover_url=data.get("cover_url"),
        )
    except (svc.BookError, ValueError) as e:
        return _error(str(e), 400, "invalid_book")
    return jsonify(_book_json(book)), 201


@bp.route("/<int:bid>", methods=["PUT"])
@api_auth_required("employee", "admin")
def update_book(bid):
    b = svc.get_book(bid)
    if not b:
        return _error("book not found", 404, "not_found")
    data = request.get_json(silent=True) or {}
    fields = {k: v for k, v in data.items() if k in {
        "title", "isbn", "publisher", "publish_year", "language", "pages",
        "description", "category_id", "total_copies", "shelf_location", "cover_url", "author_ids"
    }}
    svc.update_book(b, **fields)
    return jsonify(_book_json(b))


@bp.route("/<int:bid>", methods=["DELETE"])
@api_auth_required("employee", "admin")
def delete_book(bid):
    b = svc.get_book(bid)
    if not b:
        return _error("book not found", 404, "not_found")
    svc.delete_book(b)
    return jsonify({"message": "deleted"})
