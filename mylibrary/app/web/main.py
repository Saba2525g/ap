"""Main web routes (placeholder — will be expanded in Stage 6)."""
from flask import Blueprint, render_template_string

bp = Blueprint("web_main", __name__)


@bp.route("/")
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head><meta charset="UTF-8"><title>MyLibrary</title></head>
    <body style="font-family: Tahoma; text-align: center; padding: 50px;">
        <h1>📚 MyLibrary</h1>
        <p>پروژه در حال ساخت است...</p>
        <p style="color: green;">✅ Application factory works!</p>
    </body>
    </html>
    """)
