# MoodFlow - Recommendation Engine

from datetime import datetime, timedelta


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


# Task suggestions for each emotion
TASK_SUGGESTIONS = {
    'Happy': [
        {'title': 'Start a new creative project', 'category': 'Personal', 'priority': 'High'},
        {'title': 'Tackle that challenging work task', 'category': 'Work', 'priority': 'High'},
        {'title': 'Learn something new', 'category': 'Study', 'priority': 'Medium'},
        {'title': 'Go for an energetic workout', 'category': 'Health', 'priority': 'Medium'},
        {'title': 'Connect with friends or family', 'category': 'Personal', 'priority': 'Low'}
    ],
    'Sad': [
        {'title': 'Take a gentle walk outside', 'category': 'Health', 'priority': 'Low'},
        {'title': 'Journal your feelings', 'category': 'Personal', 'priority': 'Low'},
        {'title': 'Watch a comforting movie', 'category': 'Personal', 'priority': 'Low'},
        {'title': 'Do some light stretching', 'category': 'Health', 'priority': 'Low'},
        {'title': 'Call a supportive friend', 'category': 'Personal', 'priority': 'Medium'}
    ],
    'Tired': [
        {'title': 'Take a power nap (20 min)', 'category': 'Health', 'priority': 'High'},
        {'title': 'Do simple, routine tasks', 'category': 'Work', 'priority': 'Low'},
        {'title': 'Drink water and have a healthy snack', 'category': 'Health', 'priority': 'Medium'},
        {'title': 'Review notes instead of active learning', 'category': 'Study', 'priority': 'Low'},
        {'title': 'Light organizing or cleaning', 'category': 'Personal', 'priority': 'Low'}
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
        {'title': 'Go for a calming walk', 'category': 'Health', 'priority': 'Medium'}
    ],
    'Neutral': [
        {'title': 'Plan your week ahead', 'category': 'Personal', 'priority': 'Medium'},
        {'title': 'Work on medium-priority tasks', 'category': 'Work', 'priority': 'Medium'},
        {'title': 'Study or read for 30 minutes', 'category': 'Study', 'priority': 'Medium'},
        {'title': 'Light exercise or yoga', 'category': 'Health', 'priority': 'Medium'},
        {'title': 'Organize your workspace', 'category': 'Personal', 'priority': 'Low'}
    ]
}


# Score = Category (57%) + Priority (43%)
CATEGORY_WEIGHT = 57
PRIORITY_WEIGHT = 14.33


def get_priority_values(priority_preference):
    """Get priority scores based on emotion preference."""
    if priority_preference == 'High':
        return {'High': 3, 'Medium': 2, 'Low': 1}
    elif priority_preference == 'Low':
        return {'Low': 3, 'Medium': 2, 'High': 1}
    else:
        return {'Medium': 3, 'High': 2, 'Low': 2}


def calculate_task_score(task, emotion_name):
    """Calculate task score based on emotion (0-100)."""
    weights = EMOTION_WEIGHTS.get(emotion_name)
    if not weights:
        weights = EMOTION_WEIGHTS['Neutral']
    
    # Category score
    category = task.get('category', 'Personal')
    if category in weights:
        category_weight = weights[category]
    else:
        category_weight = 0.5
    category_score = category_weight * CATEGORY_WEIGHT
    
    # Priority score
    priority_preference = weights.get('priority', 'Medium')
    priority_values = get_priority_values(priority_preference)
    priority = task.get('priority', 'Medium')
    if priority in priority_values:
        priority_value = priority_values[priority]
    else:
        priority_value = 2
    priority_score = priority_value * PRIORITY_WEIGHT
    
    # Total score
    total_score = category_score + priority_score
    if total_score > 100:
        total_score = 100
    if total_score < 0:
        total_score = 0
    
    return total_score


def bubble_sort_by_score(items, descending):
    """Sort items by score using bubble sort."""
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            should_swap = False
            if descending:
                if items[j]['score'] > items[i]['score']:
                    should_swap = True
            else:
                if items[j]['score'] < items[i]['score']:
                    should_swap = True
            if should_swap:
                temp = items[i]
                items[i] = items[j]
                items[j] = temp
    return items


def get_recommended_tasks_from_repo(user_id, emotion_name, limit, task_date):
    """Get recommended tasks for a user based on emotion."""
    import repository
    
    tasks = repository.get_incomplete_tasks_by_user(user_id, task_date)
    
    scored_tasks = []
    for task in tasks:
        score = calculate_task_score(task, emotion_name)
        scored_tasks.append({'task': task, 'score': score})
    
    scored_tasks = bubble_sort_by_score(scored_tasks, True)
    
    result = []
    count = 0
    for item in scored_tasks:
        if count >= limit:
            break
        result.append({'task': item['task'], 'score': item['score']})
        count = count + 1
    
    return result


def get_suggested_tasks(emotion_name, limit):
    """Get suggested tasks for an emotion."""
    if emotion_name in TASK_SUGGESTIONS:
        suggestions = TASK_SUGGESTIONS[emotion_name]
    else:
        suggestions = TASK_SUGGESTIONS['Neutral']
    
    weights = EMOTION_WEIGHTS.get(emotion_name)
    if not weights:
        weights = EMOTION_WEIGHTS['Neutral']
    
    scored_suggestions = []
    for suggestion in suggestions:
        score = calculate_task_score(suggestion, emotion_name)
        scored_suggestions.append({'suggestion': suggestion, 'score': score})
    
    scored_suggestions = bubble_sort_by_score(scored_suggestions, True)
    
    result = []
    count = 0
    for item in scored_suggestions:
        if count >= limit:
            break
        suggestion_copy = dict(item['suggestion'])
        suggestion_copy['score'] = round(item['score'], 1)
        result.append(suggestion_copy)
        count = count + 1
    
    return result


def get_emotion_statistics_from_repo(user_id, days):
    """Calculate emotion statistics for a user."""
    import repository
    import static_data
    
    start_date = datetime.now() - timedelta(days=days)
    start_date_str = start_date.strftime('%Y-%m-%d')
    history = repository.get_emotion_history_since(user_id, start_date_str)
    
    emotion_counts = {}
    daily_emotions = {}
    
    for entry in history:
        emotion = static_data.get_emotion_by_id(entry['emotion_id'])
        if emotion:
            emotion_name = emotion['name']
            emotion_emoji = emotion['emoji']
            emotion_color = emotion['color']
        else:
            emotion_name = 'Unknown'
            emotion_emoji = '😐'
            emotion_color = '#95A5A6'
        
        if emotion_name in emotion_counts:
            emotion_counts[emotion_name] = emotion_counts[emotion_name] + 1
        else:
            emotion_counts[emotion_name] = 1
        
        date_str = entry['date']
        has_photo = False
        if entry.get('photo_url'):
            has_photo = True
        
        daily_emotions[date_str] = {
            'emotion': emotion_name,
            'emoji': emotion_emoji,
            'color': emotion_color,
            'has_photo': has_photo,
            'notes': entry.get('notes')
        }
    
    total = 0
    for emotion in emotion_counts:
        total = total + emotion_counts[emotion]
    
    emotion_percentages = {}
    for emotion in emotion_counts:
        count = emotion_counts[emotion]
        if total > 0:
            percentage = count / total * 100
        else:
            percentage = 0
        emotion_percentages[emotion] = percentage
    
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
