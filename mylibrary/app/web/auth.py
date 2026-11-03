"""Authentication web routes: login, register, logout, profile."""
from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.auth.forms import ChangePasswordForm, LoginForm, ProfileForm, RegisterForm
from app.auth.services import (
    AuthError,
    authenticate,
    change_password,
    register_student,
    update_profile,
)
from app.extensions import limiter

bp = Blueprint("web_auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute", methods=["POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("web_main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = authenticate(form.email.data, form.password.data)
        if not user:
            flash("ایمیل یا رمز عبور اشتباه است.", "danger")
        else:
            login_user(user, remember=form.remember_me.data)
            flash("خوش آمدید، " + user.full_name + "!", "success")
            next_url = request.args.get("next")
            if next_url and next_url.startswith("/"):
                return redirect(next_url)
            return redirect(url_for("web_main.index"))
    return render_template("auth/login.html", form=form)


@bp.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("web_main.index"))
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = register_student(
                full_name=form.full_name.data,
                email=form.email.data,
                password=form.password.data,
                student_number=form.student_number.data,
                phone=form.phone.data,
                faculty=form.faculty.data,
                major=form.major.data,
                enrollment_year=form.enrollment_year.data,
            )
        except AuthError as exc:
            flash(str(exc), "danger")
        else:
            login_user(user)
            flash("ثبت‌نام موفق! به MyLibrary خوش آمدید.", "success")
            return redirect(url_for("web_main.index"))
    return render_template("auth/register.html", form=form)


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("با موفقیت خارج شدید.", "info")
    return redirect(url_for("web_main.index"))


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        update_profile(current_user, full_name=form.full_name.data, phone=form.phone.data)
        flash("پروفایل به‌روزرسانی شد.", "success")
        return redirect(url_for("web_auth.profile"))
    return render_template("auth/profile.html", form=form)


@bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password_view():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        try:
            change_password(current_user, form.current_password.data, form.new_password.data)
        except AuthError as exc:
            flash(str(exc), "danger")
        else:
            flash("رمز عبور با موفقیت تغییر کرد.", "success")
            return redirect(url_for("web_auth.profile"))
    return render_template("auth/change_password.html", form=form)
