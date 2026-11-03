"""Application factory for MyLibrary."""
import os
from flask import Flask, render_template

from config import get_config


def create_app(config_name=None):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(get_config(config_name))

    # ---- Extensions ----
    from app.extensions import db, migrate, login_manager, csrf, limiter
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    # ---- Login manager config ----
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return db.session.get(User, int(user_id))

    login_manager.login_view = "web_auth.login"
    login_manager.login_message = "لطفاً برای دسترسی وارد شوید."
    login_manager.login_message_category = "warning"

    # ---- Register blueprints ----
    from app.web.auth import bp as web_auth_bp
    from app.web.main import bp as web_main_bp
    from app.web.books import bp as web_books_bp
    from app.web.borrowings import bp as web_borrowings_bp
    app.register_blueprint(web_auth_bp)
    app.register_blueprint(web_main_bp)
    app.register_blueprint(web_books_bp)
    app.register_blueprint(web_borrowings_bp)

    # ---- Error handlers ----
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    # ---- Make helpers available in templates ----
    @app.context_processor
    def inject_globals():
        from flask_login import current_user
        return {"current_user": current_user}

    return app
