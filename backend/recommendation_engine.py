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
    
    start_date = datetime.now() - timedelta(days=days)
    start_date_str = start_date.strftime('%Y-%m-%d')
    history = repository.get_emotion_history_since(user_id, start_date_str)
    
    emotion_counts = {}
    daily_emotions = {}
    
    for entry in history:
        emotion = repository.get_emotion_by_id(entry['emotion_id'])
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
        
        entry_date = entry['date']
        if hasattr(entry_date, 'strftime'):
            date_str = entry_date.strftime('%Y-%m-%d')
        else:
            date_str = str(entry_date)
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


# ==============================================
# Book Recommendation Algorithm
# ==============================================
# Content-Based Filtering with:
# 1. Emotion-Tag Matching (70% weight)
# 2. User Favorite History (30% weight)
# ==============================================

# Emotion to tag weight mapping
# Each emotion prefers certain tags
# Tags available: hopeful, comforting, peaceful, growth, emotional,
#                escapism, recharge, courage, new-perspective, focus
EMOTION_TAG_WEIGHTS = {
    'Happy': {
        'hopeful': 1.0,
        'growth': 0.9,
        'courage': 0.9,
        'escapism': 0.8,
        'new-perspective': 0.7,
        'focus': 0.6,
        'comforting': 0.5,
        'peaceful': 0.5,
        'recharge': 0.4,
        'emotional': 0.4
    },
    'Sad': {
        'comforting': 1.0,
        'hopeful': 0.9,
        'peaceful': 0.8,
        'recharge': 0.7,
        'emotional': 0.7,
        'growth': 0.6,
        'escapism': 0.5,
        'new-perspective': 0.4,
        'courage': 0.3,
        'focus': 0.2
    },
    'Tired': {
        'peaceful': 1.0,
        'recharge': 1.0,
        'comforting': 0.9,
        'escapism': 0.7,
        'hopeful': 0.5,
        'growth': 0.4,
        'focus': 0.4,
        'emotional': 0.3,
        'courage': 0.2,
        'new-perspective': 0.2
    },
    'Angry': {
        'peaceful': 1.0,
        'comforting': 0.9,
        'recharge': 0.8,
        'new-perspective': 0.7,
        'growth': 0.6,
        'hopeful': 0.5,
        'escapism': 0.5,
        'courage': 0.4,
        'emotional': 0.3,
        'focus': 0.2
    },
    'Stressed': {
        'peaceful': 1.0,
        'recharge': 1.0,
        'comforting': 0.9,
        'escapism': 0.8,
        'hopeful': 0.6,
        'growth': 0.5,
        'focus': 0.5,
        'new-perspective': 0.4,
        'emotional': 0.3,
        'courage': 0.2
    },
    'Neutral': {
        'new-perspective': 0.8,
        'growth': 0.8,
        'focus': 0.8,
        'hopeful': 0.7,
        'courage': 0.7,
        'comforting': 0.6,
        'peaceful': 0.6,
        'escapism': 0.5,
        'recharge': 0.5,
        'emotional': 0.5
    }
}

# Weight distribution
EMOTION_SCORE_WEIGHT = 70  # 70% for emotion-tag matching
FAVORITE_SCORE_WEIGHT = 30  # 30% for favorite history


def calculate_emotion_tag_score(book, emotion_name):
    """
    Calculate emotion-tag matching score for a book.
    Returns a score from 0 to 100 based on how well
    the book's tags match the emotion's preferred tags.
    """
    tag_weights = EMOTION_TAG_WEIGHTS.get(emotion_name)
    if not tag_weights:
        tag_weights = EMOTION_TAG_WEIGHTS['Neutral']
    
    book_tags = book.get('tags', [])
    if isinstance(book_tags, str):
        book_tags = book_tags.split(',')
    
    # Get tag slugs from tag objects
    tag_slugs = []
    for tag in book_tags:
        if isinstance(tag, dict):
            tag_slugs.append(tag.get('slug', ''))
        else:
            tag_slugs.append(tag)
    
    # Calculate total score from matching tags
    total_weight = 0
    match_count = 0
    
    for tag_slug in tag_slugs:
        if tag_slug in tag_weights:
            total_weight = total_weight + tag_weights[tag_slug]
            match_count = match_count + 1
    
    # Bonus for emotion match
    book_emotion = book.get('emotion', '')
    if book_emotion == emotion_name:
        total_weight = total_weight + 0.5
    
    # Normalize score to 0-100
    max_possible = 3.0  # Assume max 3 matching tags at weight 1.0
    score = (total_weight / max_possible) * 100
    
    if score > 100:
        score = 100
    if score < 0:
        score = 0
    
    return score


def calculate_favorite_score(book, favorite_tag_counts):
    """
    Calculate favorite-based score for a book.
    Higher score if book has tags that user frequently favorites.
    Returns a score from 0 to 100.
    """
    if not favorite_tag_counts:
        return 0
    
    book_tags = book.get('tags', [])
    if isinstance(book_tags, str):
        book_tags = book_tags.split(',')
    
    # Get tag slugs from tag objects
    tag_slugs = []
    for tag in book_tags:
        if isinstance(tag, dict):
            tag_slugs.append(tag.get('slug', ''))
        else:
            tag_slugs.append(tag)
    
    # Find max count for normalization
    max_count = 1
    for tag in favorite_tag_counts:
        if favorite_tag_counts[tag] > max_count:
            max_count = favorite_tag_counts[tag]
    
    # Calculate score based on favorite tag frequency
    total_score = 0
    for tag_slug in tag_slugs:
        if tag_slug in favorite_tag_counts:
            tag_frequency = favorite_tag_counts[tag_slug] / max_count
            total_score = total_score + (tag_frequency * 33.3)
    
    if total_score > 100:
        total_score = 100
    
    return total_score


def calculate_book_score(book, emotion_name, favorite_tag_counts):
    """
    Calculate combined recommendation score for a book.
    Total Score = Emotion Score (70%) + Favorite Score (30%)
    Returns a score from 0 to 100.
    """
    emotion_score = calculate_emotion_tag_score(book, emotion_name)
    favorite_score = calculate_favorite_score(book, favorite_tag_counts)
    
    # Weighted combination
    total_score = (emotion_score * EMOTION_SCORE_WEIGHT / 100) + (favorite_score * FAVORITE_SCORE_WEIGHT / 100)
    
    return round(total_score, 1)


def get_recommended_books(user_id, emotion_name, limit):
    """
    Get recommended books for a user based on their emotion
    and favorite history. Uses content-based filtering.
    
    Algorithm:
    1. Get all books from database
    2. Get user's favorite tag history
    3. Calculate score for each book
    4. Sort by score (descending)
    5. Return top N books
    """
    import repository
    
    # Get all books
    all_books = repository.get_all_books()
    
    # Get user's favorite tag counts
    favorite_tag_counts = repository.get_favorite_book_tags(user_id)
    
    # Get user's current favorites to exclude from recommendations
    user_favorites = repository.get_user_book_favorites(user_id)
    
    # Calculate scores for each book
    scored_books = []
    for book in all_books:
        # Skip books already in favorites
        if book['id'] in user_favorites:
            continue
        
        score = calculate_book_score(book, emotion_name, favorite_tag_counts)
        scored_books.append({
            'book': book,
            'score': score
        })
    
    # Sort by score using bubble sort (student-friendly)
    scored_books = bubble_sort_by_score(scored_books, True)
    
    # Return top N books
    result = []
    count = 0
    for item in scored_books:
        if count >= limit:
            break
        book_with_score = item['book'].copy()
        book_with_score['recommendation_score'] = item['score']
        result.append(book_with_score)
        count = count + 1
    
    return result
