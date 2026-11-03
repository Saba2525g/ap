"""WTForms for books."""
from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectMultipleField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class BookForm(FlaskForm):
    title = StringField("عنوان", validators=[DataRequired(), Length(min=1, max=255)])
    isbn = StringField("ISBN", validators=[DataRequired(), Length(min=3, max=20)])
    publisher = StringField("ناشر", validators=[Optional(), Length(max=150)])
    publish_year = IntegerField("سال انتشار", validators=[Optional(), NumberRange(min=1300, max=2100)])
    pages = IntegerField("تعداد صفحات", validators=[Optional(), NumberRange(min=1, max=20000)])
    language = StringField("زبان", validators=[Optional(), Length(max=10)], default="fa")
    total_copies = IntegerField("تعداد نسخه", validators=[DataRequired(), NumberRange(min=0, max=10000)])
    shelf_location = StringField("محل قفسه", validators=[Optional(), Length(max=60)])
    cover_url = StringField("آدرس تصویر جلد (URL)", validators=[Optional(), Length(max=500)])
    description = TextAreaField("توضیحات", validators=[Optional()])
    category_id = IntegerField("شناسه دسته (اختیاری)", validators=[Optional()])
    author_ids = SelectMultipleField("نویسنده‌ها", coerce=int, validators=[Optional()])
    submit = SubmitField("ذخیره")


class CategoryForm(FlaskForm):
    name = StringField("نام دسته", validators=[DataRequired(), Length(min=1, max=120)])
    description = TextAreaField("توضیحات", validators=[Optional()])
    submit = SubmitField("ذخیره")


class AuthorForm(FlaskForm):
    full_name = StringField("نام کامل", validators=[DataRequired(), Length(min=1, max=180)])
    nationality = StringField("ملیت", validators=[Optional(), Length(max=80)])
    birth_year = IntegerField("سال تولد", validators=[Optional(), NumberRange(min=1000, max=2100)])
    bio = TextAreaField("بیوگرافی", validators=[Optional()])
    submit = SubmitField("ذخیره")
