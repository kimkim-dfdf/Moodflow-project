from datetime import datetime, timedelta
import random

# Emotion weights for task categories
EMOTION_WEIGHTS = {
    'Happy': {'Work': 1.0, 'Study': 0.9, 'Health': 0.8, 'Personal': 0.7, 'priority': 'High'},
    'Sad': {'Personal': 1.0, 'Health': 0.8, 'Study': 0.5, 'Work': 0.4, 'priority': 'Low'},
    'Tired': {'Personal': 1.0, 'Health': 0.7, 'Study': 0.4, 'Work': 0.3, 'priority': 'Low'},
    'Angry': {'Health': 1.0, 'Personal': 0.7, 'Work': 0.5, 'Study': 0.4, 'priority': 'Medium'},
    'Stressed': {'Health': 1.0, 'Personal': 0.8, 'Work': 0.6, 'Study': 0.5, 'priority': 'Medium'},
    'Neutral': {'Work': 0.8, 'Study': 0.8, 'Health': 0.7, 'Personal': 0.7, 'priority': 'Medium'}
}

PRIORITY_SCORES = {'High': 3, 'Medium': 2, 'Low': 1}

# Task suggestions per emotion
TASK_SUGGESTIONS = {
    'Happy': [
        {'title': 'Start a new creative project', 'category': 'Personal', 'priority': 'High'},
        {'title': 'Tackle that challenging work task', 'category': 'Work', 'priority': 'High'},
        {'title': 'Learn something new', 'category': 'Study', 'priority': 'Medium'},
        {'title': 'Go for an energetic workout', 'category': 'Health', 'priority': 'Medium'},
        {'title': 'Connect with friends or family', 'category': 'Personal', 'priority': 'Low'},
    ],
    'Sad': [
        {'title': 'Take a gentle walk outside', 'category': 'Health', 'priority': 'Low'},
        {'title': 'Journal your feelings', 'category': 'Personal', 'priority': 'Low'},
        {'title': 'Watch a comforting movie', 'category': 'Personal', 'priority': 'Low'},
        {'title': 'Do some light stretching', 'category': 'Health', 'priority': 'Low'},
        {'title': 'Call a supportive friend', 'category': 'Personal', 'priority': 'Medium'},
    ],
    'Tired': [
        {'title': 'Take a power nap (20 min)', 'category': 'Health', 'priority': 'High'},
        {'title': 'Do simple, routine tasks', 'category': 'Work', 'priority': 'Low'},
        {'title': 'Drink water and have a healthy snack', 'category': 'Health', 'priority': 'Medium'},
        {'title': 'Review notes instead of active learning', 'category': 'Study', 'priority': 'Low'},
        {'title': 'Light organizing or cleaning', 'category': 'Personal', 'priority': 'Low'},
    ],
    'Angry': [
        {'title': 'Intense workout to release energy', 'category': 'Health', 'priority': 'High'},
        {'title': 'Write out your frustrations', 'category': 'Personal', 'priority': 'Medium'},
        {'title': 'Physical activity like running or boxing', 'category': 'Health', 'priority': 'High'},
        {'title': 'Deep breathing exercises', 'category': 'Health', 'priority': 'Low'},
        {'title': 'Channel energy into productive work', 'category': 'Work', 'priority': 'Medium'}
    ],
    'Stressed': [
        {'title': 'Practice meditation (10 min)', 'category': 'Health', 'priority': 'High'},
        {'title': 'Make a prioritized to-do list', 'category': 'Personal', 'priority': 'Medium'},
        {'title': 'Take a relaxing bath or shower', 'category': 'Health', 'priority': 'Low'},
        {'title': 'Break big tasks into smaller steps', 'category': 'Work', 'priority': 'High'},
        {'title': 'Go for a calming walk', 'category': 'Health', 'priority': 'Medium'},
    ],
    'Neutral': [
        {'title': 'Plan your week ahead', 'category': 'Personal', 'priority': 'Medium'},
        {'title': 'Work on medium-priority tasks', 'category': 'Work', 'priority': 'Medium'},
        {'title': 'Study or read for 30 minutes', 'category': 'Study', 'priority': 'Medium'},
        {'title': 'Light exercise or yoga', 'category': 'Health', 'priority': 'Medium'},
        {'title': 'Organize your workspace', 'category': 'Personal', 'priority': 'Low'},
    ]
}


def calculate_task_score(task, emotion_name):
    weights = EMOTION_WEIGHTS.get(emotion_name, EMOTION_WEIGHTS['Neutral'])
    
    # Category score (40%)
    cat_weight = weights.get(task.category, 0.5)
    category_score = cat_weight * 40
    
    # Priority score (35%)
    priority_match = 1.0 if task.priority == weights.get('priority') else 0.7
    p_score = PRIORITY_SCORES.get(task.priority, 2)
    priority_score = p_score * priority_match * 11.67
    
    # Urgency score (25%)
    urgency_score = 0
    if task.due_date:
        days = (task.due_date - datetime.now().date()).days
        if days <= 0:
            urgency_score = 25
        elif days <= 1:
            urgency_score = 20
        elif days <= 3:
            urgency_score = 12
        elif days <= 7:
            urgency_score = 5
    
    total = category_score + priority_score + urgency_score
    return max(0, min(100, total))


def get_recommended_tasks(db, user_id, emotion_name, limit, task_date):
    from models import Task
    
    query = Task.query.filter_by(user_id=user_id, is_completed=False)
    if task_date:
        query = query.filter_by(task_date=task_date)
    
    tasks = query.all()
    scored = [{'task': t, 'score': calculate_task_score(t, emotion_name)} for t in tasks]
    scored.sort(key=lambda x: x['score'], reverse=True)
    
    return [{'task': item['task'].to_dict(), 'score': item['score']} for item in scored[:limit]]


def get_suggested_tasks(emotion_name, limit):
    suggestions = TASK_SUGGESTIONS.get(emotion_name, TASK_SUGGESTIONS['Neutral'])
    return random.sample(suggestions, min(limit, len(suggestions)))


def get_music_recommendations(db, emotion_name, user_id, limit):
    from models import Emotion, MusicRecommendation
    
    emotion = Emotion.query.filter_by(name=emotion_name).first()
    if not emotion:
        return []
    
    music = MusicRecommendation.query.filter_by(emotion_id=emotion.id).order_by(MusicRecommendation.popularity_score.desc()).limit(limit).all()
    return [m.to_dict() for m in music]


def get_emotion_statistics(db, user_id, days):
    from models import EmotionHistory
    
    start = datetime.now().date() - timedelta(days=days)
    history = EmotionHistory.query.filter(EmotionHistory.user_id == user_id, EmotionHistory.date >= start).all()
    
    counts = {}
    daily = {}
    
    for entry in history:
        name = entry.emotion.name if entry.emotion else 'Unknown'
        counts[name] = counts.get(name, 0) + 1
        daily[entry.date.isoformat()] = {
            'emotion': name,
            'emoji': entry.emotion.emoji if entry.emotion else '😐',
            'color': entry.emotion.color if entry.emotion else '#95A5A6',
            'has_photo': bool(entry.photo_url),
            'notes': entry.notes
        }
    
    total = sum(counts.values())
    percentages = {k: (v / total * 100) if total > 0 else 0 for k, v in counts.items()}
    dominant = max(counts, key=counts.get) if counts else 'Neutral'
    
    return {
        'counts': counts,
        'percentages': percentages,
        'dominant_emotion': dominant,
        'total_entries': total,
        'daily_emotions': daily,
        'period_days': days
    }
