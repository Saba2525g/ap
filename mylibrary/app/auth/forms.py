"""WTForms for authentication & profile."""
from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, Regexp


class LoginForm(FlaskForm):
    email = StringField(
        "ایمیل",
        validators=[DataRequired(message="ایمیل الزامی است."), Email(message="ایمیل معتبر نیست."), Length(max=255)],
    )
    password = PasswordField(
        "رمز عبور",
        validators=[DataRequired(message="رمز عبور الزامی است."), Length(min=6, max=128)],
    )
    remember_me = BooleanField("مرا به خاطر بسپار")
    submit = SubmitField("ورود")


class RegisterForm(FlaskForm):
    full_name = StringField(
        "نام و نام خانوادگی",
        validators=[DataRequired(message="نام الزامی است."), Length(min=2, max=150)],
    )
    email = StringField(
        "ایمیل",
        validators=[DataRequired(), Email(message="ایمیل معتبر نیست."), Length(max=255)],
    )
    phone = StringField(
        "شماره تماس",
        validators=[Optional(), Regexp(r"^09\d{9}$", message="شماره موبایل باید با 09 شروع شود و 11 رقم باشد.")],
    )
    student_number = StringField(
        "شماره دانشجویی",
        validators=[DataRequired(message="شماره دانشجویی الزامی است."), Length(min=4, max=30)],
    )
    faculty = StringField("دانشکده", validators=[Optional(), Length(max=120)])
    major = StringField("رشته", validators=[Optional(), Length(max=120)])
    enrollment_year = IntegerField("سال ورود", validators=[Optional()])
    password = PasswordField(
        "رمز عبور",
        validators=[DataRequired(), Length(min=8, max=128, message="رمز عبور باید حداقل ۸ کاراکتر باشد.")],
    )
    confirm = PasswordField(
        "تکرار رمز عبور",
        validators=[DataRequired(), EqualTo("password", message="رمزها یکسان نیستند.")],
    )
    submit = SubmitField("ثبت‌نام")


class ProfileForm(FlaskForm):
    full_name = StringField("نام و نام خانوادگی", validators=[DataRequired(), Length(min=2, max=150)])
    phone = StringField(
        "شماره تماس",
        validators=[Optional(), Regexp(r"^09\d{9}$", message="شماره موبایل معتبر نیست.")],
    )
    submit = SubmitField("ذخیره")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("رمز فعلی", validators=[DataRequired()])
    new_password = PasswordField(
        "رمز جدید",
        validators=[DataRequired(), Length(min=8, max=128, message="رمز عبور باید حداقل ۸ کاراکتر باشد.")],
    )
    confirm = PasswordField(
        "تکرار رمز جدید",
        validators=[DataRequired(), EqualTo("new_password", message="رمزها یکسان نیستند.")],
    )
    submit = SubmitField("تغییر رمز")