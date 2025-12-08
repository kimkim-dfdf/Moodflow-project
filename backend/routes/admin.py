# ==============================================
# Admin Routes
# ==============================================

from flask import Blueprint, jsonify
from flask_login import current_user
from functools import wraps

import repository

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator to require admin access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Login required'}), 401
        if not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/stats', methods=['GET'])
@admin_required
def get_admin_stats():
    """Get overall statistics for admin dashboard."""
    user_stats = repository.get_all_users_stats()
    emotion_stats = repository.get_overall_emotion_stats()
    task_stats = repository.get_overall_task_stats()
    
    emotion_details = []
    for emotion_id, count in emotion_stats.items():
        emotion = repository.get_emotion_by_id(int(emotion_id))
        if emotion:
            emotion_details.append({
                'emotion': emotion,
                'count': count
            })
    
    return jsonify({
        'users': user_stats,
        'emotions': emotion_details,
        'tasks': task_stats,
        'total_users': len(user_stats)
    })


@admin_bp.route('/music', methods=['GET'])
@admin_required
def get_all_music_admin():
    """Get all music for admin."""
    return jsonify(repository.get_all_music())


@admin_bp.route('/books', methods=['GET'])
@admin_required
def get_all_books_admin():
    """Get all books for admin."""
    return jsonify(repository.get_all_books())


@admin_bp.route('/tags', methods=['GET'])
@admin_required
def get_all_tags_admin():
    """Get all book tags for admin."""
    return jsonify(repository.get_all_book_tags())
