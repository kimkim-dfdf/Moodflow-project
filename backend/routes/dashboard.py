# ==============================================
# Dashboard Routes
# ==============================================

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime

import repository
import recommendation_engine

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/summary', methods=['GET'])
@login_required
def get_dashboard_summary():
    """Get a summary of data for the dashboard."""
    user = current_user
    today = datetime.now().strftime('%Y-%m-%d')
    
    today_emotion = repository.get_emotion_entry_by_date(user.id, today)
    
    task_counts = repository.count_tasks(user.id)
    total_tasks = task_counts['total']
    completed_tasks = task_counts['completed']
    pending_tasks = total_tasks - completed_tasks
    
    today_tasks = repository.get_today_due_tasks(user.id, today)
    
    emotion_stats = recommendation_engine.get_emotion_statistics_from_repo(
        user.id,
        7
    )
    
    today_emotion_dict = None
    if today_emotion:
        emotion = repository.get_emotion_by_id(today_emotion['emotion_id'])
        today_emotion_dict = dict(today_emotion)
        today_emotion_dict['emotion'] = emotion
    
    return jsonify({
        'user': repository.user_to_dict(user),
        'today_emotion': today_emotion_dict,
        'task_summary': {
            'total': total_tasks,
            'completed': completed_tasks,
            'pending': pending_tasks
        },
        'today_tasks': today_tasks,
        'weekly_mood_stats': emotion_stats
    })
