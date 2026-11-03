"""Main dashboard route."""
from __future__ import annotations

from flask import Blueprint, render_template
from flask_login import current_user

from app.services import dashboard_service as dash

bp = Blueprint("web_main", __name__)


@bp.route("/")
def index():
    stats = dash.global_stats()
    chart_7d = dash.chart_borrowings_7d()
    chart_cat = dash.chart_category_pie()
    chart_status = dash.chart_borrowing_status()
    popular = dash.popular_books(5)

    student_stats_data = {}
    if current_user.is_authenticated and current_user.is_student and current_user.student:
        student_stats_data = dash.student_stats(current_user.student)

    recent = []
    if current_user.is_authenticated and current_user.role in ("admin", "employee"):
        recent = dash.recent_activities(10)

    return render_template(
        "dashboard.html",
        stats=stats,
        student_stats=student_stats_data,
        chart_7d=chart_7d,
        chart_cat=chart_cat,
        chart_status=chart_status,
        popular=popular,
        recent=recent,
    )
