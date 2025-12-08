# ==============================================
# Admin Repository
# ==============================================
# Handles admin statistics operations
# ==============================================

from models import User, Task, EmotionHistory
from repository.task_repo import count_tasks


def get_all_users_stats():
    """Get statistics for all users."""
    users = User.query.filter_by(is_admin=False).all()
    
    stats = []
    for user in users:
        user_id = user.id
        task_counts = count_tasks(user_id)
        emotion_count = EmotionHistory.query.filter_by(user_id=user_id).count()
        
        stats.append({
            'user_id': user_id,
            'username': user.username,
            'email': user.email,
            'total_tasks': task_counts['total'],
            'completed_tasks': task_counts['completed'],
            'emotion_entries': emotion_count
        })
    
    return stats


def get_overall_emotion_stats():
    """Get overall emotion statistics across all users."""
    entries = EmotionHistory.query.all()
    
    emotion_counts = {}
    for entry in entries:
        emotion_id = entry.emotion_id
        if emotion_id in emotion_counts:
            emotion_counts[emotion_id] = emotion_counts[emotion_id] + 1
        else:
            emotion_counts[emotion_id] = 1
    
    return emotion_counts


def get_overall_task_stats():
    """Get overall task statistics across all users."""
    total = Task.query.count()
    completed = Task.query.filter_by(is_completed=True).count()
    
    tasks = Task.query.all()
    category_counts = {}
    
    for task in tasks:
        category = task.category
        if category in category_counts:
            category_counts[category] = category_counts[category] + 1
        else:
            category_counts[category] = 1
    
    return {
        'total': total,
        'completed': completed,
        'pending': total - completed,
        'by_category': category_counts
    }
