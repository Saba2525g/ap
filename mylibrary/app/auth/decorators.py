"""Role-based access control decorators."""
from __future__ import annotations

from functools import wraps

from flask import abort, flash, redirect, request, url_for
from flask_login import current_user


def role_required(*allowed_roles: str):
    """Require the current user to have one of the given roles.

    - Redirects anonymous users to the login page.
    - Returns 403 for authenticated users with insufficient permissions.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("برای دسترسی باید وارد شوید.", "warning")
                return redirect(url_for("web_auth.login", next=request.path))
            if current_user.role not in allowed_roles:
                abort(403)
            return view_func(*args, **kwargs)
        return wrapped
    return decorator


def admin_required(view_func):
    """Shortcut for @role_required('admin')."""
    return role_required("admin")(view_func)


def staff_required(view_func):
    """Shortcut for employee OR admin."""
    return role_required("employee", "admin")(view_func)


def student_required(view_func):
    """Shortcut for student role."""
    return role_required("student")(view_func)