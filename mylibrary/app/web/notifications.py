"""Notification routes."""
from __future__ import annotations

from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.services import notification_service as svc

bp = Blueprint("web_notifications", __name__, url_prefix="/notifications")


@bp.route("/")
@login_required
def list_all():
    items = svc.list_for_user(current_user.id)
    unread = svc.unread_count(current_user.id)
    return render_template("notifications/list.html", items=items, unread=unread)


@bp.route("/<int:nid>/read", methods=["POST"])
@login_required
def mark_read(nid: int):
    svc.mark_read(nid, current_user.id)
    return redirect(request.referrer or url_for("web_notifications.list_all"))


@bp.route("/read-all", methods=["POST"])
@login_required
def read_all():
    svc.mark_all_read(current_user.id)
    return redirect(url_for("web_notifications.list_all"))


@bp.route("/api/unread-count")
@login_required
def api_unread_count():
    return jsonify({"count": svc.unread_count(current_user.id)})
