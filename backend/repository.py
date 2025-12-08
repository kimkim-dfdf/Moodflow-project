# ==============================================
# MoodFlow - Data Repository
# ==============================================
# This file handles all data storage operations
# Data is stored in PostgreSQL database
# Uses SQLAlchemy ORM for database operations
# ==============================================

from datetime import datetime
from models import db, User, Task, EmotionHistory, CustomMusic, CustomBook, BookFavorite


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
    task = Task(
        user_id=user_id,
        title=title,
        description=None,
        category=category,
        priority=priority,
        is_completed=False,
        due_date=None,
        due_time=None,
        task_date=task_date,
        created_at=datetime.utcnow(),
        completed_at=None,
        recommended_for_emotion=recommended_for_emotion,
        emotion_score=0.0
    )
    
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
    
    # Sort by created_at descending (newest first)
    query = query.order_by(Task.created_at.desc())
    
    tasks = query.all()
    
    # Convert to list of dictionaries
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
    
    # Convert to list of dictionaries
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
    
    # Convert to list of dictionaries
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
    # Check if entry already exists for this date
    existing = EmotionHistory.query.filter_by(user_id=user_id, date=date).first()
    
    if existing:
        # Update existing entry
        existing.emotion_id = emotion_id
        existing.recorded_at = datetime.utcnow()
        
        if notes:
            existing.notes = notes
        if photo_url:
            existing.photo_url = photo_url
        
        db.session.commit()
        return existing.to_dict()
    
    # Create new entry
    entry = EmotionHistory(
        user_id=user_id,
        emotion_id=emotion_id,
        date=date,
        notes=notes,
        photo_url=photo_url,
        recorded_at=datetime.utcnow()
    )
    
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
    
    # Convert to list of dictionaries
    result = []
    for entry in entries:
        result.append(entry.to_dict())
    
    return result


# ==============================================
# Music Operations (Admin)
# ==============================================

def get_all_custom_music():
    """Get all custom music entries."""
    music_list = CustomMusic.query.all()
    
    # Convert to list of dictionaries
    result = []
    for music in music_list:
        result.append(music.to_dict())
    
    return result


def create_music(emotion, title, artist, genre, youtube_url):
    """Create a new music recommendation."""
    music = CustomMusic(
        emotion=emotion,
        title=title,
        artist=artist,
        genre=genre,
        youtube_url=youtube_url,
        is_custom=True
    )
    
    db.session.add(music)
    db.session.commit()
    
    return music.to_dict()


def update_music(music_id, emotion, title, artist, genre, youtube_url):
    """Update an existing custom music entry."""
    music = CustomMusic.query.get(music_id)
    
    if music:
        music.emotion = emotion
        music.title = title
        music.artist = artist
        music.genre = genre
        music.youtube_url = youtube_url
        db.session.commit()
        return music.to_dict()
    
    return None


def delete_music(music_id):
    """Delete a custom music entry."""
    music = CustomMusic.query.get(music_id)
    
    if music:
        db.session.delete(music)
        db.session.commit()
        return True
    
    return False


# ==============================================
# Book Operations (Admin)
# ==============================================

def get_all_custom_books():
    """Get all custom book entries."""
    books = CustomBook.query.all()
    
    # Convert to list of dictionaries
    result = []
    for book in books:
        result.append(book.to_dict())
    
    return result


def create_book(emotion, title, author, genre, description, tags):
    """Create a new book recommendation."""
    # Convert tags list to comma-separated string
    tags_str = ','.join(tags) if isinstance(tags, list) else tags
    
    book = CustomBook(
        emotion=emotion,
        title=title,
        author=author,
        genre=genre,
        description=description,
        tags=tags_str,
        is_custom=True
    )
    
    db.session.add(book)
    db.session.commit()
    
    return book.to_dict()


def update_book(book_id, emotion, title, author, genre, description, tags):
    """Update an existing custom book entry."""
    book = CustomBook.query.get(book_id)
    
    if book:
        # Convert tags list to comma-separated string
        tags_str = ','.join(tags) if isinstance(tags, list) else tags
        
        book.emotion = emotion
        book.title = title
        book.author = author
        book.genre = genre
        book.description = description
        book.tags = tags_str
        db.session.commit()
        return book.to_dict()
    
    return None


def delete_book(book_id):
    """Delete a custom book entry."""
    book = CustomBook.query.get(book_id)
    
    if book:
        db.session.delete(book)
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
    
    # Get tasks for category counting
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
# Book Favorites Operations
# ==============================================

def get_user_favorites(user_id):
    """
    Get all favorite book IDs for a user.
    Returns a list of book IDs.
    """
    favorites = BookFavorite.query.filter_by(user_id=user_id).all()
    
    result = []
    for favorite in favorites:
        result.append(favorite.book_id)
    
    return result


def add_favorite(user_id, book_id):
    """
    Add a book to user's favorites.
    Returns True if added, False if already exists.
    """
    # Check if already in favorites
    existing = BookFavorite.query.filter_by(user_id=user_id, book_id=book_id).first()
    
    if existing:
        return False
    
    # Add new favorite
    favorite = BookFavorite(
        user_id=user_id,
        book_id=book_id,
        added_at=datetime.utcnow()
    )
    
    db.session.add(favorite)
    db.session.commit()
    
    return True


def remove_favorite(user_id, book_id):
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
# Deprecated Functions (for compatibility)
# ==============================================

def load_data():
    """
    This function is no longer needed.
    Data is now stored in PostgreSQL database.
    Kept for backward compatibility.
    """
    pass


def save_data():
    """
    This function is no longer needed.
    Data is automatically saved by SQLAlchemy.
    Kept for backward compatibility.
    """
    pass
