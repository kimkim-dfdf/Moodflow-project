# ==============================================
# MoodFlow - Data Repository (Simplified)
# ==============================================
# This file handles all data storage operations
# Data is stored in PostgreSQL database
# Uses SQLAlchemy ORM for database operations
# ==============================================

from datetime import datetime
from models import db, User, Task, EmotionHistory, BookFavorite, MusicFavorite, Emotion, Music, BookTag, Book


# ==============================================
# User Operations
# ==============================================

def get_user_by_id(user_id):
    """Find a user by their ID and return User object."""
    user = db.session.get(User, int(user_id))
    return user


def get_user_by_email(email):
    """Find a user by their email address and return User object."""
    user = User.query.filter_by(email=email).first()
    return user


def check_user_password(user, password):
    """
    Check if the provided password is correct.
    Simple string comparison (no hashing for demo).
    """
    if user.password == password:
        return True
    return False


def user_to_dict(user):
    """
    Convert a user object to a dictionary for API responses.
    Excludes password from the response.
    """
    return user.to_dict()


def get_user_by_username(username):
    """Find a user by their username and return User object."""
    user = User.query.filter_by(username=username).first()
    return user


def update_user(user_id, new_username):
    """
    Update a user's username.
    """
    user = db.session.get(User, int(user_id))
    if user:
        user.username = new_username
        db.session.commit()
        return user
    return None


# ==============================================
# Task Operations
# ==============================================

def create_task(user_id, title, category, priority, task_date, recommended_for_emotion):
    """
    Create a new task for a user.
    """
    task = Task()
    task.user_id = user_id
    task.title = title
    task.description = None
    task.category = category
    task.priority = priority
    task.is_completed = False
    task.due_date = None
    task.due_time = None
    task.task_date = task_date
    task.created_at = datetime.utcnow()
    task.completed_at = None
    task.recommended_for_emotion = recommended_for_emotion
    task.emotion_score = 0.0
    
    db.session.add(task)
    db.session.commit()
    
    return task.to_dict()


def get_tasks_by_user(user_id, task_date):
    """
    Get all tasks for a user.
    Optionally filter by task_date.
    Results are sorted by created_at (newest first).
    """
    query = Task.query.filter_by(user_id=user_id)
    
    if task_date:
        query = query.filter_by(task_date=task_date)
    
    query = query.order_by(Task.created_at.desc())
    
    tasks = query.all()
    
    result = []
    for task in tasks:
        result.append(task.to_dict())
    
    return result


def get_incomplete_tasks_by_user(user_id, task_date):
    """
    Get all incomplete tasks for a user.
    Optionally filter by task_date.
    """
    query = Task.query.filter_by(user_id=user_id, is_completed=False)
    
    if task_date:
        query = query.filter_by(task_date=task_date)
    
    tasks = query.all()
    
    result = []
    for task in tasks:
        result.append(task.to_dict())
    
    return result


def get_task_by_id(task_id, user_id):
    """Find a specific task by ID and user ID."""
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if task:
        return task.to_dict()
    return None


def get_existing_task(user_id, title, task_date):
    """
    Check if a task with the same title already exists for this date.
    Used to prevent duplicate tasks.
    """
    task = Task.query.filter_by(
        user_id=user_id,
        title=title,
        task_date=task_date,
        is_completed=False
    ).first()
    
    if task:
        return task.to_dict()
    return None


def update_task(task_id, user_id, is_completed):
    """
    Update a task's completion status.
    Sets completed_at timestamp when completed.
    """
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    
    if task:
        task.is_completed = is_completed
        
        if is_completed:
            task.completed_at = datetime.utcnow()
        else:
            task.completed_at = None
        
        db.session.commit()
        return task.to_dict()
    
    return None


def delete_task(task_id, user_id):
    """
    Delete a task.
    Returns True if deleted, False if not found.
    """
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    
    if task:
        db.session.delete(task)
        db.session.commit()
        return True
    
    return False


def count_tasks(user_id):
    """
    Count total and completed tasks for a user.
    Returns a dictionary with 'total' and 'completed' counts.
    """
    total = Task.query.filter_by(user_id=user_id).count()
    completed = Task.query.filter_by(user_id=user_id, is_completed=True).count()
    
    return {
        'total': total,
        'completed': completed
    }


def get_today_due_tasks(user_id, today):
    """
    Get tasks that are due today and not completed.
    """
    tasks = Task.query.filter_by(
        user_id=user_id,
        due_date=today,
        is_completed=False
    ).all()
    
    result = []
    for task in tasks:
        result.append(task.to_dict())
    
    return result


# ==============================================
# Emotion History Operations
# ==============================================

def create_emotion_entry(user_id, emotion_id, date, notes, photo_url):
    """
    Create or update an emotion entry for a specific date.
    If an entry already exists for this date, update it.
    """
    existing = EmotionHistory.query.filter_by(user_id=user_id, date=date).first()
    
    if existing:
        existing.emotion_id = emotion_id
        existing.recorded_at = datetime.utcnow()
        
        if notes:
            existing.notes = notes
        if photo_url:
            existing.photo_url = photo_url
        
        db.session.commit()
        return existing.to_dict()
    
    entry = EmotionHistory()
    entry.user_id = user_id
    entry.emotion_id = emotion_id
    entry.date = date
    entry.notes = notes
    entry.photo_url = photo_url
    entry.recorded_at = datetime.utcnow()
    
    db.session.add(entry)
    db.session.commit()
    
    return entry.to_dict()


def get_emotion_entry_by_date(user_id, date):
    """Find an emotion entry for a specific date."""
    entry = EmotionHistory.query.filter_by(user_id=user_id, date=date).first()
    if entry:
        return entry.to_dict()
    return None


def get_emotion_history_since(user_id, start_date):
    """
    Get emotion entries since a specific date.
    Used for calculating statistics.
    """
    entries = EmotionHistory.query.filter(
        EmotionHistory.user_id == user_id,
        EmotionHistory.date >= start_date
    ).all()
    
    result = []
    for entry in entries:
        result.append(entry.to_dict())
    
    return result


# ==============================================
# Book Favorites Operations
# ==============================================

def get_user_book_favorites(user_id):
    """
    Get all favorite book IDs for a user.
    Returns a list of book IDs.
    """
    favorites = BookFavorite.query.filter_by(user_id=user_id).all()
    
    result = []
    for favorite in favorites:
        result.append(favorite.book_id)
    
    return result


def add_book_favorite(user_id, book_id):
    """
    Add a book to user's favorites.
    Returns True if added, False if already exists.
    """
    existing = BookFavorite.query.filter_by(user_id=user_id, book_id=book_id).first()
    
    if existing:
        return False
    
    favorite = BookFavorite()
    favorite.user_id = user_id
    favorite.book_id = book_id
    favorite.added_at = datetime.utcnow()
    
    db.session.add(favorite)
    db.session.commit()
    
    return True


def remove_book_favorite(user_id, book_id):
    """
    Remove a book from user's favorites.
    Returns True if removed, False if not found.
    """
    favorite = BookFavorite.query.filter_by(user_id=user_id, book_id=book_id).first()
    
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return True
    
    return False


# ==============================================
# Music Favorites Operations
# ==============================================

def get_user_music_favorites(user_id):
    """
    Get all favorite music IDs for a user.
    Returns a list of music IDs.
    """
    favorites = MusicFavorite.query.filter_by(user_id=user_id).all()
    
    result = []
    for favorite in favorites:
        result.append(favorite.music_id)
    
    return result


def add_music_favorite(user_id, music_id):
    """
    Add a music to user's favorites.
    Returns True if added, False if already exists.
    """
    existing = MusicFavorite.query.filter_by(user_id=user_id, music_id=music_id).first()
    
    if existing:
        return False
    
    favorite = MusicFavorite()
    favorite.user_id = user_id
    favorite.music_id = music_id
    favorite.added_at = datetime.utcnow()
    
    db.session.add(favorite)
    db.session.commit()
    
    return True


def remove_music_favorite(user_id, music_id):
    """
    Remove a music from user's favorites.
    Returns True if removed, False if not found.
    """
    favorite = MusicFavorite.query.filter_by(user_id=user_id, music_id=music_id).first()
    
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return True
    
    return False


# ==============================================
# Admin Statistics Operations
# ==============================================

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


# ==============================================
# Emotion Operations
# ==============================================

def get_all_emotions():
    """Get all emotions from database."""
    emotions = Emotion.query.all()
    
    result = []
    for emotion in emotions:
        result.append(emotion.to_dict())
    
    return result


def get_emotion_by_id(emotion_id):
    """Find an emotion by its ID."""
    emotion = db.session.get(Emotion, int(emotion_id))
    if emotion:
        return emotion.to_dict()
    return None


def get_emotion_by_name(emotion_name):
    """Find an emotion by its name."""
    emotion = Emotion.query.filter_by(name=emotion_name).first()
    if emotion:
        return emotion.to_dict()
    return None


# ==============================================
# Music Operations
# ==============================================

def get_all_music():
    """Get all music from database."""
    music_list = Music.query.all()
    
    result = []
    for music in music_list:
        result.append(music.to_dict())
    
    return result


def get_music_by_emotion(emotion_name, limit):
    """
    Get music recommendations for a specific emotion.
    Returns up to 'limit' songs.
    """
    query = Music.query.filter_by(emotion=emotion_name)
    music_list = query.all()
    
    result = []
    for music in music_list:
        result.append(music.to_dict())
    
    if limit and limit < len(result):
        return result[:limit]
    
    return result


# ==============================================
# Book Tag Operations
# ==============================================

def get_all_book_tags():
    """Get all available book tags."""
    tags = BookTag.query.all()
    
    result = []
    for tag in tags:
        result.append(tag.to_dict())
    
    return result


def get_tag_by_slug(slug):
    """Find a tag by its slug."""
    tag = BookTag.query.filter_by(slug=slug).first()
    if tag:
        return tag.to_dict()
    return None


# ==============================================
# Book Operations
# ==============================================

def get_all_books():
    """Get all books from database."""
    books = Book.query.all()
    tags_cache = get_all_tags_as_dict()
    
    result = []
    for book in books:
        book_dict = book.to_dict()
        book_dict['tags'] = get_tag_objects_for_book(book_dict, tags_cache)
        result.append(book_dict)
    
    return result


def get_books_by_tags(tag_slugs, limit):
    """
    Get books that match ALL of the specified tags (AND logic).
    """
    books = Book.query.all()
    tags_cache = get_all_tags_as_dict()
    
    if not tag_slugs:
        result = []
        for book in books:
            book_dict = book.to_dict()
            book_dict['tags'] = get_tag_objects_for_book(book_dict, tags_cache)
            result.append(book_dict)
        
        if limit and limit < len(result):
            return result[:limit]
        return result
    
    result = []
    
    for book in books:
        book_tags = book.tags.split(',') if book.tags else []
        
        match_count = 0
        for tag in tag_slugs:
            if tag in book_tags:
                match_count = match_count + 1
        
        if match_count == len(tag_slugs):
            book_dict = book.to_dict()
            book_dict['tags'] = get_tag_objects_for_book(book_dict, tags_cache)
            result.append(book_dict)
    
    if limit and limit < len(result):
        return result[:limit]
    
    return result


def get_all_tags_as_dict():
    """
    Get all book tags as a dictionary for fast lookup.
    Key: slug, Value: tag dictionary
    """
    all_tags = BookTag.query.all()
    
    result = {}
    for tag in all_tags:
        result[tag.slug] = tag.to_dict()
    
    return result


def get_tag_objects_for_book(book_dict, tags_cache=None):
    """
    Get full tag objects for a book's tags.
    Converts tag slugs to full tag dictionaries.
    Uses cache to avoid N+1 queries.
    """
    if tags_cache is None:
        tags_cache = get_all_tags_as_dict()
    
    result = []
    
    tag_slugs = book_dict.get('tags', [])
    if isinstance(tag_slugs, str):
        tag_slugs = tag_slugs.split(',')
    
    for tag_slug in tag_slugs:
        if tag_slug in tags_cache:
            result.append(tags_cache[tag_slug])
    
    return result


