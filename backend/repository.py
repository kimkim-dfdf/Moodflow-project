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
# Legacy function names for compatibility
# ==============================================

def get_user_favorites(user_id):
    """Legacy function name for book favorites."""
    return get_user_book_favorites(user_id)


def add_favorite(user_id, book_id):
    """Legacy function name for adding book favorite."""
    return add_book_favorite(user_id, book_id)


def remove_favorite(user_id, book_id):
    """Legacy function name for removing book favorite."""
    return remove_book_favorite(user_id, book_id)


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
    
    result = []
    for book in books:
        book_dict = book.to_dict()
        book_dict['tags'] = get_tag_objects_for_book(book_dict)
        result.append(book_dict)
    
    return result


def get_books_by_tags(tag_slugs, limit):
    """
    Get books that match ALL of the specified tags (AND logic).
    """
    books = Book.query.all()
    
    if not tag_slugs:
        result = []
        for book in books:
            book_dict = book.to_dict()
            book_dict['tags'] = get_tag_objects_for_book(book_dict)
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
            book_dict['tags'] = get_tag_objects_for_book(book_dict)
            result.append(book_dict)
    
    if limit and limit < len(result):
        return result[:limit]
    
    return result


def get_tag_objects_for_book(book_dict):
    """
    Get full tag objects for a book's tags.
    Converts tag slugs to full tag dictionaries.
    """
    result = []
    
    tag_slugs = book_dict.get('tags', [])
    if isinstance(tag_slugs, str):
        tag_slugs = tag_slugs.split(',')
    
    for tag_slug in tag_slugs:
        tag = BookTag.query.filter_by(slug=tag_slug).first()
        if tag:
            result.append(tag.to_dict())
    
    return result


# ==============================================
# Seed Data Functions
# ==============================================

def seed_emotions():
    """Seed emotion data into database."""
    emotions_data = [
        {'id': 1, 'name': 'Happy', 'emoji': '😊', 'color': '#FFD93D'},
        {'id': 2, 'name': 'Sad', 'emoji': '😢', 'color': '#6B7FD7'},
        {'id': 3, 'name': 'Tired', 'emoji': '😴', 'color': '#8B4513'},
        {'id': 4, 'name': 'Angry', 'emoji': '😠', 'color': '#FF6B6B'},
        {'id': 5, 'name': 'Stressed', 'emoji': '😰', 'color': '#FF9F43'},
        {'id': 6, 'name': 'Neutral', 'emoji': '😐', 'color': '#95A5A6'}
    ]
    
    for data in emotions_data:
        existing = Emotion.query.filter_by(name=data['name']).first()
        if not existing:
            emotion = Emotion()
            emotion.name = data['name']
            emotion.emoji = data['emoji']
            emotion.color = data['color']
            db.session.add(emotion)
    
    db.session.commit()


def seed_music():
    """Seed music data into database."""
    music_data = [
        {'emotion': 'Happy', 'title': 'Happy', 'artist': 'Pharrell Williams', 'genre': 'Pop', 'youtube_url': 'https://www.youtube.com/watch?v=ZbZSe6N_BXs'},
        {'emotion': 'Happy', 'title': 'Good as Hell', 'artist': 'Lizzo', 'genre': 'Pop', 'youtube_url': 'https://www.youtube.com/watch?v=SmbmeOgWsqE'},
        {'emotion': 'Happy', 'title': 'Walking on Sunshine', 'artist': 'Katrina and the Waves', 'genre': 'Pop Rock', 'youtube_url': 'https://www.youtube.com/watch?v=iPUmE-tne5U'},
        {'emotion': 'Happy', 'title': 'Uptown Funk', 'artist': 'Bruno Mars', 'genre': 'Funk Pop', 'youtube_url': 'https://www.youtube.com/watch?v=OPf0YbXqDm0'},
        {'emotion': 'Sad', 'title': 'Someone Like You', 'artist': 'Adele', 'genre': 'Pop Ballad', 'youtube_url': 'https://www.youtube.com/watch?v=hLQl3WQQoQ0'},
        {'emotion': 'Sad', 'title': 'Fix You', 'artist': 'Coldplay', 'genre': 'Alternative Rock', 'youtube_url': 'https://www.youtube.com/watch?v=k4V3Mo61fJM'},
        {'emotion': 'Sad', 'title': 'Hurt', 'artist': 'Johnny Cash', 'genre': 'Country', 'youtube_url': 'https://www.youtube.com/watch?v=8AHCfZTRGiI'},
        {'emotion': 'Sad', 'title': 'The Night We Met', 'artist': 'Lord Huron', 'genre': 'Indie Folk', 'youtube_url': 'https://www.youtube.com/watch?v=KtlgYxa6BMU'},
        {'emotion': 'Tired', 'title': 'Weightless', 'artist': 'Marconi Union', 'genre': 'Ambient', 'youtube_url': 'https://www.youtube.com/watch?v=UfcAVejslrU'},
        {'emotion': 'Tired', 'title': 'Clair de Lune', 'artist': 'Debussy', 'genre': 'Classical', 'youtube_url': 'https://www.youtube.com/watch?v=CvFH_6DNRCY'},
        {'emotion': 'Tired', 'title': 'Sunset Lover', 'artist': 'Petit Biscuit', 'genre': 'Electronic', 'youtube_url': 'https://www.youtube.com/watch?v=wuCK-oiE3rM'},
        {'emotion': 'Tired', 'title': 'Sleep', 'artist': 'Max Richter', 'genre': 'Ambient Classical', 'youtube_url': 'https://www.youtube.com/watch?v=4UAqmSJhN9M'},
        {'emotion': 'Angry', 'title': 'Break Stuff', 'artist': 'Limp Bizkit', 'genre': 'Nu Metal', 'youtube_url': 'https://www.youtube.com/watch?v=ZpUYjpKg9KY'},
        {'emotion': 'Angry', 'title': 'Killing in the Name', 'artist': 'Rage Against the Machine', 'genre': 'Rock', 'youtube_url': 'https://www.youtube.com/watch?v=bWXazVhlyxQ'},
        {'emotion': 'Angry', 'title': 'Bodies', 'artist': 'Drowning Pool', 'genre': 'Metal', 'youtube_url': 'https://www.youtube.com/watch?v=04F4xlWSFh0'},
        {'emotion': 'Angry', 'title': 'Chop Suey!', 'artist': 'System of a Down', 'genre': 'Metal', 'youtube_url': 'https://www.youtube.com/watch?v=CSvFpBOe8eY'},
        {'emotion': 'Stressed', 'title': 'Breathe Me', 'artist': 'Sia', 'genre': 'Pop', 'youtube_url': 'https://www.youtube.com/watch?v=wHOH3VMHVx8'},
        {'emotion': 'Stressed', 'title': 'Orinoco Flow', 'artist': 'Enya', 'genre': 'New Age', 'youtube_url': 'https://www.youtube.com/watch?v=LTrk4X9ACtw'},
        {'emotion': 'Stressed', 'title': 'Ocean Eyes', 'artist': 'Billie Eilish', 'genre': 'Electropop', 'youtube_url': 'https://www.youtube.com/watch?v=viimfQi_pUw'},
        {'emotion': 'Stressed', 'title': 'Strawberry Swing', 'artist': 'Coldplay', 'genre': 'Alternative Rock', 'youtube_url': 'https://www.youtube.com/watch?v=h3pJZSTQqIg'},
        {'emotion': 'Neutral', 'title': 'Lovely Day', 'artist': 'Bill Withers', 'genre': 'Soul', 'youtube_url': 'https://www.youtube.com/watch?v=bEeaS6fuUoA'},
        {'emotion': 'Neutral', 'title': 'Here Comes the Sun', 'artist': 'The Beatles', 'genre': 'Rock', 'youtube_url': 'https://www.youtube.com/watch?v=KQetemT1sWc'},
        {'emotion': 'Neutral', 'title': 'Budapest', 'artist': 'George Ezra', 'genre': 'Folk Pop', 'youtube_url': 'https://www.youtube.com/watch?v=VHrLPs3_1Fs'},
        {'emotion': 'Neutral', 'title': 'Electric Feel', 'artist': 'MGMT', 'genre': 'Indie Electronic', 'youtube_url': 'https://www.youtube.com/watch?v=MmZexg8sxyk'}
    ]
    
    existing_count = Music.query.count()
    if existing_count == 0:
        for data in music_data:
            music = Music()
            music.emotion = data['emotion']
            music.title = data['title']
            music.artist = data['artist']
            music.genre = data['genre']
            music.youtube_url = data['youtube_url']
            db.session.add(music)
        
        db.session.commit()


def seed_book_tags():
    """Seed book tag data into database."""
    tags_data = [
        {'name': 'Hopeful', 'slug': 'hopeful', 'color': '#22c55e'},
        {'name': 'Comforting', 'slug': 'comforting', 'color': '#f97316'},
        {'name': 'Peaceful', 'slug': 'peaceful', 'color': '#06b6d4'},
        {'name': 'Growth', 'slug': 'growth', 'color': '#8b5cf6'},
        {'name': 'Emotional', 'slug': 'emotional', 'color': '#ec4899'},
        {'name': 'Escapism', 'slug': 'escapism', 'color': '#6366f1'},
        {'name': 'Recharge', 'slug': 'recharge', 'color': '#14b8a6'},
        {'name': 'Courage', 'slug': 'courage', 'color': '#dc2626'},
        {'name': 'New Perspective', 'slug': 'new-perspective', 'color': '#0d9488'},
        {'name': 'Focus', 'slug': 'focus', 'color': '#3b82f6'}
    ]
    
    for data in tags_data:
        existing = BookTag.query.filter_by(slug=data['slug']).first()
        if not existing:
            tag = BookTag()
            tag.name = data['name']
            tag.slug = data['slug']
            tag.color = data['color']
            db.session.add(tag)
    
    db.session.commit()


def seed_books():
    """Seed book data into database."""
    books_data = [
        {'emotion': 'Happy', 'title': 'The Alchemist', 'author': 'Paulo Coelho', 'genre': 'Fiction', 'description': 'A magical story about following your dreams', 'tags': 'hopeful,growth,new-perspective'},
        {'emotion': 'Happy', 'title': 'Big Magic', 'author': 'Elizabeth Gilbert', 'genre': 'Self-Help', 'description': 'Creative living beyond fear', 'tags': 'growth,focus,hopeful'},
        {'emotion': 'Happy', 'title': 'The Happiness Project', 'author': 'Gretchen Rubin', 'genre': 'Self-Help', 'description': 'A year-long journey to discover happiness', 'tags': 'hopeful,growth,recharge'},
        {'emotion': 'Happy', 'title': 'Yes Please', 'author': 'Amy Poehler', 'genre': 'Memoir', 'description': 'Hilarious and inspiring stories', 'tags': 'hopeful,courage,emotional'},
        {'emotion': 'Sad', 'title': 'When Breath Becomes Air', 'author': 'Paul Kalanithi', 'genre': 'Memoir', 'description': 'A profound reflection on life and death', 'tags': 'emotional,comforting,growth'},
        {'emotion': 'Sad', 'title': 'The Year of Magical Thinking', 'author': 'Joan Didion', 'genre': 'Memoir', 'description': 'Processing grief and loss', 'tags': 'comforting,emotional,peaceful'},
        {'emotion': 'Sad', 'title': 'Tiny Beautiful Things', 'author': 'Cheryl Strayed', 'genre': 'Self-Help', 'description': 'Advice on life and love', 'tags': 'comforting,emotional,peaceful'},
        {'emotion': 'Sad', 'title': 'Norwegian Wood', 'author': 'Haruki Murakami', 'genre': 'Fiction', 'description': 'A story of love and melancholy', 'tags': 'emotional,escapism,peaceful'},
        {'emotion': 'Tired', 'title': 'The Little Prince', 'author': 'Antoine de Saint-Exupery', 'genre': 'Fiction', 'description': 'A gentle tale with deep meaning', 'tags': 'hopeful,escapism,new-perspective'},
        {'emotion': 'Tired', 'title': 'Winnie-the-Pooh', 'author': 'A.A. Milne', 'genre': 'Fiction', 'description': 'Comforting adventures in the Hundred Acre Wood', 'tags': 'comforting,recharge,peaceful'},
        {'emotion': 'Tired', 'title': 'The House in the Cerulean Sea', 'author': 'TJ Klune', 'genre': 'Fantasy', 'description': 'A cozy, heartwarming fantasy', 'tags': 'escapism,comforting,peaceful'},
        {'emotion': 'Tired', 'title': 'Hygge: The Danish Art of Living', 'author': 'Meik Wiking', 'genre': 'Lifestyle', 'description': 'Finding comfort in simple pleasures', 'tags': 'recharge,peaceful,comforting'},
        {'emotion': 'Angry', 'title': 'The Art of War', 'author': 'Sun Tzu', 'genre': 'Philosophy', 'description': 'Ancient wisdom on strategy', 'tags': 'courage,focus,growth'},
        {'emotion': 'Angry', 'title': 'Rage', 'author': 'Bob Woodward', 'genre': 'Non-Fiction', 'description': 'Understanding power and politics', 'tags': 'emotional,courage,comforting'},
        {'emotion': 'Angry', 'title': 'Anger: Wisdom for Cooling the Flames', 'author': 'Thich Nhat Hanh', 'genre': 'Self-Help', 'description': 'Buddhist approach to managing anger', 'tags': 'peaceful,new-perspective,growth'}
    ]
    
    existing_count = Book.query.count()
    if existing_count == 0:
        for data in books_data:
            book = Book()
            book.emotion = data['emotion']
            book.title = data['title']
            book.author = data['author']
            book.genre = data['genre']
            book.description = data['description']
            book.tags = data['tags']
            db.session.add(book)
        
        db.session.commit()


def seed_all_static_data():
    """Seed all static data (emotions, music, tags, books)."""
    seed_emotions()
    seed_book_tags()
    seed_music()
    seed_books()
