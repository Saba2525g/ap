"""Borrowing routes: request, approve, reject, return, reserve."""
from __future__ import annotations

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.auth.decorators import staff_required
from app.extensions import db
from app.models.borrowing import Borrowing, Reservation
from app.services import borrowing_service as svc
from app.services.book_service import get_book

bp = Blueprint("web_borrowings", __name__, url_prefix="/borrowings")


@bp.route("/my")
@login_required
def my():
    if not current_user.is_student:
        flash("این بخش مخصوص دانشجویان است.", "warning")
        return redirect(url_for("web_main.index"))
    student = current_user.student
    if not student:
        flash("پروفایل دانشجویی یافت نشد.", "danger")
        return redirect(url_for("web_main.index"))

    borrowings = db.session.query(Borrowing).filter(
        Borrowing.student_id == student.id
    ).order_by(Borrowing.requested_at.desc()).all()

    reservations = db.session.query(Reservation).filter(
        Reservation.student_id == student.id
    ).order_by(Reservation.reserved_at.desc()).all()

    return render_template("borrowings/my.html", borrowings=borrowings,
                           reservations=reservations)


@bp.route("/requests")
@staff_required
def requests_list():
    items = db.session.query(Borrowing).filter(
        Borrowing.status == "pending"
    ).order_by(Borrowing.requested_at).all()
    return render_template("borrowings/requests.html", items=items)


@bp.route("/all")
@staff_required
def all_list():
    status = request.args.get("status", "")
    q = db.session.query(Borrowing)
    if status:
        q = q.filter(Borrowing.status == status)
    items = q.order_by(Borrowing.requested_at.desc()).limit(200).all()
    return render_template("borrowings/all.html", items=items,
                           status=status, stats=svc.stats())


@bp.route("/request/<int:book_id>", methods=["POST"])
@login_required
def request_borrow(book_id):
    if not current_user.is_student:
        flash("فقط دانشجویان می‌توانند امانت بگیرند.", "warning")
        return redirect(url_for("web_books.detail", book_id=book_id))
    book = get_book(book_id)
    if not book:
        abort(404)
    try:
        svc.request_borrow(current_user.student, book)
    except svc.BorrowError as exc:
        flash(str(exc), "danger")
    else:
        flash("درخواست امانت ثبت شد. منتظر تأیید باشید.", "success")
    return redirect(url_for("web_books.detail", book_id=book_id))


@bp.route("/<int:borrow_id>/approve", methods=["POST"])
@staff_required
def approve(borrow_id):
    b = db.session.get(Borrowing, borrow_id)
    if not b:
        abort(404)
    try:
        svc.approve_borrow(b, current_user)
    except svc.BorrowError as exc:
        flash(str(exc), "danger")
    else:
        flash("امانت تأیید شد.", "success")
    return redirect(url_for("web_borrowings.requests_list"))


@bp.route("/<int:borrow_id>/reject", methods=["POST"])
@staff_required
def reject(borrow_id):
    b = db.session.get(Borrowing, borrow_id)
    if not b:
        abort(404)
    reason = request.form.get("reason", "").strip()
    try:
        svc.reject_borrow(b, current_user, reason)
    except svc.BorrowError as exc:
        flash(str(exc), "danger")
    else:
        flash("درخواست رد شد.", "info")
    return redirect(url_for("web_borrowings.requests_list"))


@bp.route("/<int:borrow_id>/return", methods=["POST"])
@staff_required
def return_one(borrow_id):
    b = db.session.get(Borrowing, borrow_id)
    if not b:
        abort(404)
    try:
        svc.return_book(b, current_user)
    except svc.BorrowError as exc:
        flash(str(exc), "danger")
    else:
        flash("بازگشت کتاب ثبت شد.", "success")
    return redirect(url_for("web_borrowings.all_list"))


@bp.route("/reserve/<int:book_id>", methods=["POST"])
@login_required
def reserve(book_id):
    if not current_user.is_student:
        flash("فقط دانشجویان می‌توانند رزرو کنند.", "warning")
        return redirect(url_for("web_books.detail", book_id=book_id))
    book = get_book(book_id)
    if not book:
        abort(404)
    try:
        svc.reserve_book(current_user.student, book)
    except svc.BorrowError as exc:
        flash(str(exc), "danger")
    else:
        flash("رزرو ثبت شد.", "success")
    return redirect(url_for("web_books.detail", book_id=book_id))
