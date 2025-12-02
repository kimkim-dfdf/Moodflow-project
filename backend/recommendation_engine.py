from datetime import datetime, timedelta
import random

# Emotion weights for task categories
EMOTION_WEIGHTS = {
    'Happy': {
        'Work': 1.0,
        'Study': 0.9,
        'Health': 0.8,
        'Personal': 0.7,
        'priority': 'High'
    },
    'Sad': {
        'Personal': 1.0,
        'Health': 0.8,
        'Study': 0.5,
        'Work': 0.4,
        'priority': 'Low'
    },
    'Tired': {
        'Personal': 1.0,
        'Health': 0.7,
        'Study': 0.4,
        'Work': 0.3,
        'priority': 'Low'
    },
    'Angry': {
        'Health': 1.0,
        'Personal': 0.7,
        'Work': 0.5,
        'Study': 0.4,
        'priority': 'Medium'
    },
    'Stressed': {
        'Health': 1.0,
        'Personal': 0.8,
        'Work': 0.6,
        'Study': 0.5,
        'priority': 'Medium'
    },
    'Neutral': {
        'Work': 0.8,
        'Study': 0.8,
        'Health': 0.7,
        'Personal': 0.7,
        'priority': 'Medium'
    }
}

PRIORITY_SCORES = {
    'High': 3,
    'Medium': 2,
    'Low': 1
}

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
    # Get weights for this emotion
    weights = EMOTION_WEIGHTS.get(emotion_name)
    if not weights:
        weights = EMOTION_WEIGHTS['Neutral']
    
    # Category score (40% weight)
    category = task.category
    if category in weights:
        cat_weight = weights[category]
    else:
        cat_weight = 0.5
    category_score = cat_weight * 40
    
    # Priority score (35% weight)
    priority_pref = weights.get('priority', 'Medium')
    
    if task.priority == priority_pref:
        priority_match = 1.0
    else:
        priority_match = 0.7
    
    if task.priority in PRIORITY_SCORES:
        p_score = PRIORITY_SCORES[task.priority]
    else:
        p_score = 2
    priority_score = p_score * priority_match * 11.67
    
    # Urgency score (25% weight)
    urgency_score = 0
    if task.due_date:
        today = datetime.now().date()
        days_until_due = (task.due_date - today).days
        
        if days_until_due <= 0:
            urgency_score = 25
        elif days_until_due <= 1:
            urgency_score = 20
        elif days_until_due <= 3:
            urgency_score = 12
        elif days_until_due <= 7:
            urgency_score = 5
        else:
            urgency_score = 0
    
    # Calculate total score
    total = category_score + priority_score + urgency_score
    
    # Keep between 0 and 100
    if total > 100:
        total = 100
    if total < 0:
        total = 0
    
    return total


def get_recommended_tasks(db, user_id, emotion_name, limit, task_date):
    from models import Task
    
    # Get incomplete tasks
    query = Task.query.filter_by(user_id=user_id, is_completed=False)
    if task_date:
        query = query.filter_by(task_date=task_date)
    
    tasks = query.all()
    
    # Calculate score for each task
    scored_tasks = []
    for task in tasks:
        score = calculate_task_score(task, emotion_name)
        scored_tasks.append({'task': task, 'score': score})
    
    # Sort by score (highest first) using bubble sort
    for i in range(len(scored_tasks)):
        for j in range(i + 1, len(scored_tasks)):
            if scored_tasks[j]['score'] > scored_tasks[i]['score']:
                temp = scored_tasks[i]
                scored_tasks[i] = scored_tasks[j]
                scored_tasks[j] = temp
    
    # Return top results
    result = []
    count = 0
    for item in scored_tasks:
        if count >= limit:
            break
        result.append({
            'task': item['task'].to_dict(),
            'score': item['score']
        })
        count = count + 1
    
    return result


def get_suggested_tasks(emotion_name, limit):
    # Get suggestions for this emotion
    if emotion_name in TASK_SUGGESTIONS:
        suggestions = TASK_SUGGESTIONS[emotion_name]
    else:
        suggestions = TASK_SUGGESTIONS['Neutral']
    
    # Return random selection
    if limit > len(suggestions):
        limit = len(suggestions)
    
    selected = random.sample(suggestions, limit)
    return selected


def get_music_recommendations(db, emotion_name, user_id, limit):
    from models import Emotion, MusicRecommendation
    
    # Find emotion
    emotion = Emotion.query.filter_by(name=emotion_name).first()
    if not emotion:
        return []
    
    # Get music for this emotion
    music_list = MusicRecommendation.query.filter_by(emotion_id=emotion.id).order_by(MusicRecommendation.popularity_score.desc()).limit(limit).all()
    
    # Convert to list
    result = []
    for music in music_list:
        result.append(music.to_dict())
    
    return result


def get_emotion_statistics(db, user_id, days):
    from models import EmotionHistory
    
    start_date = datetime.now().date() - timedelta(days=days)
    
    # Get history
    history = EmotionHistory.query.filter(
        EmotionHistory.user_id == user_id,
        EmotionHistory.date >= start_date
    ).all()
    
    # Count emotions
    emotion_counts = {}
    daily_emotions = {}
    
    for entry in history:
        # Get emotion name
        if entry.emotion:
            emo_name = entry.emotion.name
        else:
            emo_name = 'Unknown'
        
        # Count it
        if emo_name in emotion_counts:
            emotion_counts[emo_name] = emotion_counts[emo_name] + 1
        else:
            emotion_counts[emo_name] = 1
        
        # Store daily data
        date_str = entry.date.isoformat()
        daily_emotions[date_str] = {
            'emotion': emo_name,
            'emoji': entry.emotion.emoji if entry.emotion else '😐',
            'color': entry.emotion.color if entry.emotion else '#95A5A6',
            'has_photo': True if entry.photo_url else False,
            'notes': entry.notes
        }
    
    # Calculate total
    total = 0
    for emotion in emotion_counts:
        total = total + emotion_counts[emotion]
    
    # Calculate percentages
    emotion_percentages = {}
    for emotion in emotion_counts:
        count = emotion_counts[emotion]
        if total > 0:
            pct = count / total * 100
        else:
            pct = 0
        emotion_percentages[emotion] = pct
    
    # Find most common emotion
    dominant_emotion = 'Neutral'
    max_count = 0
    for emotion in emotion_counts:
        if emotion_counts[emotion] > max_count:
            max_count = emotion_counts[emotion]
            dominant_emotion = emotion
    
    return {
        'counts': emotion_counts,
        'percentages': emotion_percentages,
        'dominant_emotion': dominant_emotion,
        'total_entries': total,
        'daily_emotions': daily_emotions,
        'period_days': days
    }
