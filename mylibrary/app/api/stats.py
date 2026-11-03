"""Stats API endpoints."""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.api._helpers import api_auth_required
from app.services import dashboard_service as dash

bp = Blueprint("api_stats", __name__, url_prefix="/api/v1/stats")


@bp.route("/global", methods=["GET"])
def global_stats():
    return jsonify(dash.global_stats())


@bp.route("/charts", methods=["GET"])
def charts():
    return jsonify({
        "borrowings_7d": dash.chart_borrowings_7d(),
        "category_pie": dash.chart_category_pie(),
        "status_breakdown": dash.chart_borrowing_status(),
    })


@bp.route("/me", methods=["GET"])
@api_auth_required()
def me_stats():
    u = request.current_user
    if u.is_student and u.student:
        return jsonify(dash.student_stats(u.student))
    return jsonify({})
