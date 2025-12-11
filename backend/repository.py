# ==============================================
# MoodFlow - Data Repository (Simplified)
# ==============================================
# This file handles all data storage operations
# Data is stored in PostgreSQL database
# Uses SQLAlchemy ORM for database operations
# ==============================================

from datetime import datetime
from models import db, User, Task, EmotionHistory, Emotion, Music, BookTag, Book, BookReview


# ==============================================
# User Operations
# ==============================================

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
    task.category = category
    task.priority = priority
    task.is_completed = False
    task.task_date = task_date
    task.created_at = datetime.utcnow()
    task.completed_at = None
    task.recommended_for_emotion = recommended_for_emotion
    
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
        task_date=today,
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


def get_music_by_id(music_id):
    """Get a single music track by ID."""
    music = db.session.get(Music, int(music_id))
    if music:
        return music.to_dict()
    return None


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


# ==============================================
# Admin Music CRUD Operations
# ==============================================

def create_music(emotion, title, artist, genre, youtube_url):
    """
    Create a new music entry.
    Returns the created music as dictionary.
    """
    new_music = Music(
        emotion=emotion,
        title=title,
        artist=artist,
        genre=genre,
        youtube_url=youtube_url
    )
    db.session.add(new_music)
    db.session.commit()
    
    return new_music.to_dict()


def update_music(music_id, emotion, title, artist, genre, youtube_url):
    """
    Update an existing music entry.
    Returns the updated music as dictionary, or None if not found.
    """
    music = Music.query.filter_by(id=music_id).first()
    
    if music is None:
        return None
    
    music.emotion = emotion
    music.title = title
    music.artist = artist
    music.genre = genre
    music.youtube_url = youtube_url
    db.session.commit()
    
    return music.to_dict()


def delete_music(music_id):
    """
    Delete a music entry by ID.
    Returns True if deleted, False if not found.
    """
    music = Music.query.filter_by(id=music_id).first()
    
    if music is None:
        return False
    
    db.session.delete(music)
    db.session.commit()
    return True


# ==============================================
# Admin Book CRUD Operations
# ==============================================

def create_book(emotion, title, author, genre, description, tags):
    """
    Create a new book entry.
    tags should be a list of tag slugs.
    Returns the created book as dictionary.
    """
    tags_str = ','.join(tags) if tags else ''
    
    new_book = Book(
        emotion=emotion,
        title=title,
        author=author,
        genre=genre,
        description=description,
        tags=tags_str
    )
    db.session.add(new_book)
    db.session.commit()
    
    result = new_book.to_dict()
    result['tags'] = get_tag_objects_for_book(result)
    return result


def update_book(book_id, emotion, title, author, genre, description, tags):
    """
    Update an existing book entry.
    tags should be a list of tag slugs.
    Returns the updated book as dictionary, or None if not found.
    """
    book = Book.query.filter_by(id=book_id).first()
    
    if book is None:
        return None
    
    tags_str = ','.join(tags) if tags else ''
    
    book.emotion = emotion
    book.title = title
    book.author = author
    book.genre = genre
    book.description = description
    book.tags = tags_str
    db.session.commit()
    
    result = book.to_dict()
    result['tags'] = get_tag_objects_for_book(result)
    return result


def delete_book(book_id):
    """
    Delete a book entry by ID.
    Returns True if deleted, False if not found.
    """
    book = Book.query.filter_by(id=book_id).first()
    
    if book is None:
        return False
    
    db.session.delete(book)
    db.session.commit()
    return True


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


# ==============================================
# Book Review Operations
# ==============================================

def get_reviews_for_book(book_id):
    """
    Get all reviews for a specific book.
    Returns reviews with user information.
    """
    reviews = BookReview.query.filter_by(book_id=book_id).order_by(BookReview.created_at.desc()).all()
    
    result = []
    for review in reviews:
        review_dict = review.to_dict()
        user = db.session.get(User, review.user_id)
        if user:
            review_dict['username'] = user.username
        else:
            review_dict['username'] = 'Unknown'
        result.append(review_dict)
    
    return result


def get_user_review_for_book(user_id, book_id):
    """
    Get a specific user's review for a book.
    Returns None if no review exists.
    """
    review = BookReview.query.filter_by(user_id=user_id, book_id=book_id).first()
    if review:
        return review.to_dict()
    return None


def create_book_review(user_id, book_id, rating, content):
    """
    Create a new book review.
    Each user can only have one review per book.
    """
    existing = BookReview.query.filter_by(user_id=user_id, book_id=book_id).first()
    if existing:
        return None
    
    review = BookReview()
    review.user_id = user_id
    review.book_id = book_id
    review.rating = rating
    review.content = content
    review.created_at = datetime.utcnow()
    
    db.session.add(review)
    db.session.commit()
    
    result = review.to_dict()
    user = db.session.get(User, user_id)
    if user:
        result['username'] = user.username
    
    return result


def update_book_review(review_id, user_id, rating, content):
    """
    Update an existing book review.
    Only the review owner can update it.
    """
    review = BookReview.query.filter_by(id=review_id, user_id=user_id).first()
    if review is None:
        return None
    
    review.rating = rating
    review.content = content
    db.session.commit()
    
    result = review.to_dict()
    user = db.session.get(User, user_id)
    if user:
        result['username'] = user.username
    
    return result


def delete_book_review(review_id, user_id):
    """
    Delete a book review.
    Only the review owner can delete it.
    """
    review = BookReview.query.filter_by(id=review_id, user_id=user_id).first()
    if review is None:
        return False
    
    db.session.delete(review)
    db.session.commit()
    return True


def get_popular_books(limit=10):
    """
    Get books sorted by number of reviews (most reviewed first).
    Returns books with their review count.
    """
    books = Book.query.all()
    tags_cache = get_all_tags_as_dict()
    
    books_with_counts = []
    for book in books:
        review_count = BookReview.query.filter_by(book_id=book.id).count()
        book_dict = book.to_dict()
        book_dict['tags'] = get_tag_objects_for_book(book_dict, tags_cache)
        book_dict['review_count'] = review_count
        books_with_counts.append(book_dict)
    
    for i in range(len(books_with_counts)):
        for j in range(i + 1, len(books_with_counts)):
            if books_with_counts[j]['review_count'] > books_with_counts[i]['review_count']:
                temp = books_with_counts[i]
                books_with_counts[i] = books_with_counts[j]
                books_with_counts[j] = temp
    
    if limit and limit < len(books_with_counts):
        return books_with_counts[:limit]
    
    return books_with_counts


# ==============================================
# Music Review Functions
# ==============================================

def get_reviews_for_music(music_id):
    """
    Get all reviews for a specific music track.
    Returns reviews with user information.
    """
    from models import MusicReview
    reviews = MusicReview.query.filter_by(music_id=music_id).order_by(MusicReview.created_at.desc()).all()
    
    result = []
    for review in reviews:
        review_dict = review.to_dict()
        user = db.session.get(User, review.user_id)
        if user:
            review_dict['username'] = user.username
        else:
            review_dict['username'] = 'Unknown'
        result.append(review_dict)
    
    return result


def create_music_review(user_id, music_id, rating, content):
    """
    Create a new music review.
    Each user can only have one review per music track.
    """
    from models import MusicReview
    existing = MusicReview.query.filter_by(user_id=user_id, music_id=music_id).first()
    if existing:
        return None
    
    review = MusicReview()
    review.user_id = user_id
    review.music_id = music_id
    review.rating = rating
    review.content = content
    review.created_at = datetime.utcnow()
    
    db.session.add(review)
    db.session.commit()
    
    result = review.to_dict()
    user = db.session.get(User, user_id)
    if user:
        result['username'] = user.username
    
    return result


def delete_music_review(review_id, user_id):
    """
    Delete a music review.
    Only the review owner can delete it.
    """
    from models import MusicReview
    review = MusicReview.query.filter_by(id=review_id, user_id=user_id).first()
    if review is None:
        return False
    
    db.session.delete(review)
    db.session.commit()
    return True


