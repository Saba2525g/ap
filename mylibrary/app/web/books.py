"""Book catalog, detail, and management routes."""
from __future__ import annotations

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user

from app.auth.decorators import staff_required
from app.services import book_service as svc
from app.validators.book_forms import AuthorForm, BookForm, CategoryForm

bp = Blueprint("web_books", __name__, url_prefix="/books")


@bp.route("/")
def catalog():
    q = request.args.get("q", "").strip()
    cat = request.args.get("category", type=int)
    lang = request.args.get("language", "").strip() or None
    avail = request.args.get("available") == "1"
    page = max(1, request.args.get("page", 1, type=int))
    per_page = 12
    items, total = svc.search_books(q=q or None, category_id=cat, language=lang,
                                    available_only=avail, limit=per_page,
                                    offset=(page - 1) * per_page)
    total_pages = max(1, (total + per_page - 1) // per_page)
    return render_template("books/catalog.html", books=items, total=total, page=page,
                           total_pages=total_pages, categories=svc.list_categories(),
                           q=q, selected_cat=cat, selected_lang=lang or "",
                           available_only=avail)


@bp.route("/<int:book_id>")
def detail(book_id):
    book = svc.get_book(book_id)
    if not book or (not book.is_active and not current_user.is_authenticated):
        abort(404)
    return render_template("books/detail.html", book=book)


@bp.route("/new", methods=["GET", "POST"])
@staff_required
def create():
    form = BookForm()
    form.author_ids.choices = [(a.id, a.full_name) for a in svc.list_authors()]
    if form.validate_on_submit():
        try:
            book = svc.create_book(
                title=form.title.data, isbn=form.isbn.data,
                total_copies=form.total_copies.data,
                author_ids=form.author_ids.data or [],
                category_id=form.category_id.data or None,
                description=form.description.data, publisher=form.publisher.data,
                publish_year=form.publish_year.data, language=form.language.data or "fa",
                pages=form.pages.data, shelf_location=form.shelf_location.data,
                cover_url=form.cover_url.data,
            )
        except svc.BookError as exc:
            flash(str(exc), "danger")
        else:
            flash("کتاب ثبت شد.", "success")
            return redirect(url_for("web_books.detail", book_id=book.id))
    return render_template("books/form.html", form=form, mode="create")


@bp.route("/<int:book_id>/edit", methods=["GET", "POST"])
@staff_required
def edit(book_id):
    book = svc.get_book(book_id)
    if not book:
        abort(404)
    form = BookForm(obj=book)
    form.author_ids.choices = [(a.id, a.full_name) for a in svc.list_authors()]
    if request.method == "GET":
        form.author_ids.data = [link.author_id for link in book.author_links]
        form.category_id.data = book.category_id
    if form.validate_on_submit():
        svc.update_book(
            book, title=form.title.data, isbn=form.isbn.data,
            total_copies=form.total_copies.data,
            available_copies=min(book.available_copies, form.total_copies.data),
            author_ids=form.author_ids.data or [],
            category_id=form.category_id.data or None,
            description=form.description.data, publisher=form.publisher.data,
            publish_year=form.publish_year.data, language=form.language.data or "fa",
            pages=form.pages.data, shelf_location=form.shelf_location.data,
            cover_url=form.cover_url.data,
        )
        flash("کتاب به‌روزرسانی شد.", "success")
        return redirect(url_for("web_books.detail", book_id=book.id))
    return render_template("books/form.html", form=form, mode="edit", book=book)


@bp.route("/<int:book_id>/delete", methods=["POST"])
@staff_required
def delete(book_id):
    book = svc.get_book(book_id)
    if not book:
        abort(404)
    svc.delete_book(book)
    flash("کتاب حذف شد.", "info")
    return redirect(url_for("web_books.catalog"))


@bp.route("/manage")
@staff_required
def manage():
    q = request.args.get("q", "").strip()
    items, total = svc.search_books(q=q or None, include_inactive=True, limit=200)
    return render_template("books/manage.html", books=items, total=total, q=q, stats=svc.stats())


@bp.route("/categories", methods=["GET", "POST"])
@staff_required
def categories():
    form = CategoryForm()
    if form.validate_on_submit():
        try:
            svc.create_category(form.name.data, form.description.data)
        except svc.BookError as exc:
            flash(str(exc), "danger")
        else:
            flash("دسته اضافه شد.", "success")
            return redirect(url_for("web_books.categories"))
    return render_template("books/categories.html", form=form, categories=svc.list_categories())


@bp.route("/authors", methods=["GET", "POST"])
@staff_required
def authors():
    form = AuthorForm()
    if form.validate_on_submit():
        try:
            svc.create_author(form.full_name.data, form.bio.data,
                              form.nationality.data, form.birth_year.data)
        except svc.BookError as exc:
            flash(str(exc), "danger")
        else:
            flash("نویسنده اضافه شد.", "success")
            return redirect(url_for("web_books.authors"))
    return render_template("books/authors.html", form=form, authors=svc.list_authors())
