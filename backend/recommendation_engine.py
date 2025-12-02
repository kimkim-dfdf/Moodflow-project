from datetime import datetime, timedelta

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


def get_priority_values(priority_pref):
    if priority_pref == 'High':
        return {'High': 3, 'Medium': 2, 'Low': 1}
    elif priority_pref == 'Low':
        return {'Low': 3, 'Medium': 2, 'High': 1}
    else:
        return {'Medium': 3, 'High': 2, 'Low': 2}


def calculate_task_score(task, emotion_name):
    weights = EMOTION_WEIGHTS.get(emotion_name)
    if not weights:
        weights = EMOTION_WEIGHTS['Neutral']
    
    category = task.category
    if category in weights:
        cat_weight = weights[category]
    else:
        cat_weight = 0.5
    category_score = cat_weight * 57
    
    priority_pref = weights.get('priority', 'Medium')
    priority_values = get_priority_values(priority_pref)
    
    if task.priority in priority_values:
        p_score = priority_values[task.priority]
    else:
        p_score = 2
    priority_score = p_score * 14.33
    
    total = category_score + priority_score
    
    if total > 100:
        total = 100
    if total < 0:
        total = 0
    
    return total


def bubble_sort_by_score(items, descending):
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


def get_recommended_tasks(db, user_id, emotion_name, limit, task_date):
    from models import Task
    
    query = Task.query.filter_by(user_id=user_id, is_completed=False)
    if task_date:
        query = query.filter_by(task_date=task_date)
    
    tasks = query.all()
    
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
        result.append({
            'task': item['task'].to_dict(),
            'score': item['score']
        })
        count = count + 1
    
    return result


def get_suggested_tasks(emotion_name, limit):
    if emotion_name in TASK_SUGGESTIONS:
        suggestions = TASK_SUGGESTIONS[emotion_name]
    else:
        suggestions = TASK_SUGGESTIONS['Neutral']
    
    weights = EMOTION_WEIGHTS.get(emotion_name)
    if not weights:
        weights = EMOTION_WEIGHTS['Neutral']
    
    scored_suggestions = []
    for suggestion in suggestions:
        category = suggestion.get('category', 'Personal')
        if category in weights:
            cat_weight = weights[category]
        else:
            cat_weight = 0.5
        category_score = cat_weight * 57
        
        priority_pref = weights.get('priority', 'Medium')
        priority = suggestion.get('priority', 'Medium')
        priority_values = get_priority_values(priority_pref)
        
        if priority in priority_values:
            p_score = priority_values[priority]
        else:
            p_score = 2
        priority_score = p_score * 14.33
        
        total = category_score + priority_score
        scored_suggestions.append({'suggestion': suggestion, 'score': total})
    
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


def get_emotion_statistics(db, user_id, days):
    from models import EmotionHistory
    import static_data
    
    start_date = datetime.now().date() - timedelta(days=days)
    
    history = EmotionHistory.query.filter(
        EmotionHistory.user_id == user_id,
        EmotionHistory.date >= start_date
    ).all()
    
    emotion_counts = {}
    daily_emotions = {}
    
    for entry in history:
        emotion = static_data.get_emotion_by_id(entry.emotion_id)
        if emotion:
            emo_name = emotion['name']
            emo_emoji = emotion['emoji']
            emo_color = emotion['color']
        else:
            emo_name = 'Unknown'
            emo_emoji = '😐'
            emo_color = '#95A5A6'
        
        if emo_name in emotion_counts:
            emotion_counts[emo_name] = emotion_counts[emo_name] + 1
        else:
            emotion_counts[emo_name] = 1
        
        date_str = entry.date.isoformat()
        has_photo = False
        if entry.photo_url:
            has_photo = True
        
        daily_emotions[date_str] = {
            'emotion': emo_name,
            'emoji': emo_emoji,
            'color': emo_color,
            'has_photo': has_photo,
            'notes': entry.notes
        }
    
    total = 0
    for emotion in emotion_counts:
        total = total + emotion_counts[emotion]
    
    emotion_percentages = {}
    for emotion in emotion_counts:
        count = emotion_counts[emotion]
        if total > 0:
            pct = count / total * 100
        else:
            pct = 0
        emotion_percentages[emotion] = pct
    
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
