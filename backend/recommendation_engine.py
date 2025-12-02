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
    
    # Category score (57% weight)
    category = task.category
    if category in weights:
        cat_weight = weights[category]
    else:
        cat_weight = 0.5
    category_score = cat_weight * 57
    
    # Priority score (43% weight)
    # Score is based on emotion's preferred priority
    priority_pref = weights.get('priority', 'Medium')
    
    # Create priority scores based on emotion preference
    # The preferred priority gets 3 points, others get less
    if priority_pref == 'High':
        # Happy, energetic - prefer difficult tasks
        priority_values = {'High': 3, 'Medium': 2, 'Low': 1}
    elif priority_pref == 'Low':
        # Tired, sad - prefer easy tasks
        priority_values = {'Low': 3, 'Medium': 2, 'High': 1}
    else:
        # Neutral, angry, stressed - prefer medium tasks
        priority_values = {'Medium': 3, 'High': 2, 'Low': 2}
    
    if task.priority in priority_values:
        p_score = priority_values[task.priority]
    else:
        p_score = 2
    priority_score = p_score * 14.33
    
    # Calculate total score
    total = category_score + priority_score
    
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
    
    # Get weights for this emotion
    weights = EMOTION_WEIGHTS.get(emotion_name)
    if not weights:
        weights = EMOTION_WEIGHTS['Neutral']
    
    # Calculate score for each suggestion
    scored_suggestions = []
    for suggestion in suggestions:
        # Category score (57% weight)
        category = suggestion.get('category', 'Personal')
        if category in weights:
            cat_weight = weights[category]
        else:
            cat_weight = 0.5
        category_score = cat_weight * 57
        
        # Priority score (43% weight)
        priority_pref = weights.get('priority', 'Medium')
        priority = suggestion.get('priority', 'Medium')
        
        if priority_pref == 'High':
            priority_values = {'High': 3, 'Medium': 2, 'Low': 1}
        elif priority_pref == 'Low':
            priority_values = {'Low': 3, 'Medium': 2, 'High': 1}
        else:
            priority_values = {'Medium': 3, 'High': 2, 'Low': 2}
        
        if priority in priority_values:
            p_score = priority_values[priority]
        else:
            p_score = 2
        priority_score = p_score * 14.33
        
        total = category_score + priority_score
        scored_suggestions.append({'suggestion': suggestion, 'score': total})
    
    # Sort by score (highest first) using bubble sort
    for i in range(len(scored_suggestions)):
        for j in range(i + 1, len(scored_suggestions)):
            if scored_suggestions[j]['score'] > scored_suggestions[i]['score']:
                temp = scored_suggestions[i]
                scored_suggestions[i] = scored_suggestions[j]
                scored_suggestions[j] = temp
    
    # Return top results
    result = []
    count = 0
    for item in scored_suggestions:
        if count >= limit:
            break
        item['suggestion']['score'] = round(item['score'], 1)
        result.append(item['suggestion'])
        count = count + 1
    
    return result


def get_emotion_statistics(db, user_id, days):
    from models import EmotionHistory
    import static_data
    
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
        # Get emotion from static data
        emotion = static_data.get_emotion_by_id(entry.emotion_id)
        if emotion:
            emo_name = emotion['name']
            emo_emoji = emotion['emoji']
            emo_color = emotion['color']
        else:
            emo_name = 'Unknown'
            emo_emoji = '😐'
            emo_color = '#95A5A6'
        
        # Count it
        if emo_name in emotion_counts:
            emotion_counts[emo_name] = emotion_counts[emo_name] + 1
        else:
            emotion_counts[emo_name] = 1
        
        # Store daily data
        date_str = entry.date.isoformat()
        daily_emotions[date_str] = {
            'emotion': emo_name,
            'emoji': emo_emoji,
            'color': emo_color,
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
