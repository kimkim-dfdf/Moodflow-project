# ==============================================
# MoodFlow - Routes Package
# ==============================================

from .auth import auth_bp
from .emotions import emotions_bp
from .tasks import tasks_bp
from .music import music_bp
from .books import books_bp
from .admin import admin_bp
from .dashboard import dashboard_bp
from .uploads import uploads_bp
from .profile import profile_bp


def register_routes(app):
    """Register all blueprints with the Flask app."""
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(emotions_bp, url_prefix='/api/emotions')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    app.register_blueprint(music_bp, url_prefix='/api/music')
    app.register_blueprint(books_bp, url_prefix='/api/books')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(uploads_bp, url_prefix='/api')
    app.register_blueprint(profile_bp, url_prefix='/api/user')
