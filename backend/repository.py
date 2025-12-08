# ==============================================
# MoodFlow - Data Repository (Production)
# ==============================================

from datetime import datetime, date
from models import db, User, Task, EmotionHistory, BookFavorite, MusicFavorite, Emotion, Music, BookTag, Book, Quote
import random


# ==============================================
# User Operations
# ==============================================

def get_user_by_id(user_id):
    return db.session.get(User, int(user_id))


def get_user_by_email(email):
    return User.query.filter_by(email=email).first()


def check_user_password(user, password):
    if user.password == password:
        return True
    return False


def user_to_dict(user):
    return user.to_dict()


def get_user_by_username(username):
    return User.query.filter_by(username=username).first()


def update_user(user_id, new_username):
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
    task = Task()
    task.user_id = user_id
    task.title = title
    task.category = category
    task.priority = priority
    task.is_completed = False
    
    if task_date:
        if isinstance(task_date, str):
            task.task_date = date.fromisoformat(task_date)
        else:
            task.task_date = task_date
    
    if recommended_for_emotion:
        emotion = Emotion.query.filter_by(name=recommended_for_emotion).first()
        if emotion:
            task.emotion_id = emotion.id
    
    db.session.add(task)
    db.session.commit()
    
    return task.to_dict()


def get_tasks_by_user(user_id, task_date):
    query = Task.query.filter_by(user_id=user_id)
    
    if task_date:
        if isinstance(task_date, str):
            task_date = date.fromisoformat(task_date)
        query = query.filter_by(task_date=task_date)
    
    query = query.order_by(Task.created_at.desc())
    tasks = query.all()
    
    result = []
    for task in tasks:
        result.append(task.to_dict())
    
    return result


def get_incomplete_tasks_by_user(user_id, task_date):
    query = Task.query.filter_by(user_id=user_id, is_completed=False)
    
    if task_date:
        if isinstance(task_date, str):
            task_date = date.fromisoformat(task_date)
        query = query.filter_by(task_date=task_date)
    
    tasks = query.all()
    
    result = []
    for task in tasks:
        result.append(task.to_dict())
    
    return result


def get_task_by_id(task_id, user_id):
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if task:
        return task.to_dict()
    return None


def get_existing_task(user_id, title, task_date):
    if isinstance(task_date, str):
        task_date = date.fromisoformat(task_date)
    
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
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    
    if task:
        db.session.delete(task)
        db.session.commit()
        return True
    
    return False


def count_tasks(user_id):
    total = Task.query.filter_by(user_id=user_id).count()
    completed = Task.query.filter_by(user_id=user_id, is_completed=True).count()
    
    return {
        'total': total,
        'completed': completed
    }


def get_today_due_tasks(user_id, today):
    if isinstance(today, str):
        today = date.fromisoformat(today)
    
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

def create_emotion_entry(user_id, emotion_id, entry_date, notes, photo_url):
    if isinstance(entry_date, str):
        entry_date = date.fromisoformat(entry_date)
    
    existing = EmotionHistory.query.filter_by(user_id=user_id, date=entry_date).first()
    
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
    entry.date = entry_date
    entry.notes = notes
    entry.photo_url = photo_url
    
    db.session.add(entry)
    db.session.commit()
    
    return entry.to_dict()


def get_emotion_entry_by_date(user_id, entry_date):
    if isinstance(entry_date, str):
        entry_date = date.fromisoformat(entry_date)
    
    entry = EmotionHistory.query.filter_by(user_id=user_id, date=entry_date).first()
    if entry:
        return entry.to_dict()
    return None


def get_emotion_history_since(user_id, start_date):
    if isinstance(start_date, str):
        start_date = date.fromisoformat(start_date)
    
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
    favorites = BookFavorite.query.filter_by(user_id=user_id).all()
    
    result = []
    for favorite in favorites:
        result.append(favorite.book_id)
    
    return result


def add_book_favorite(user_id, book_id):
    existing = BookFavorite.query.filter_by(user_id=user_id, book_id=book_id).first()
    
    if existing:
        return False
    
    favorite = BookFavorite()
    favorite.user_id = user_id
    favorite.book_id = book_id
    
    db.session.add(favorite)
    db.session.commit()
    
    return True


def remove_book_favorite(user_id, book_id):
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
    favorites = MusicFavorite.query.filter_by(user_id=user_id).all()
    
    result = []
    for favorite in favorites:
        result.append(favorite.music_id)
    
    return result


def add_music_favorite(user_id, music_id):
    existing = MusicFavorite.query.filter_by(user_id=user_id, music_id=music_id).first()
    
    if existing:
        return False
    
    favorite = MusicFavorite()
    favorite.user_id = user_id
    favorite.music_id = music_id
    
    db.session.add(favorite)
    db.session.commit()
    
    return True


def remove_music_favorite(user_id, music_id):
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
    users = User.query.filter_by(is_admin=False).all()
    
    stats = []
    for user in users:
        task_counts = count_tasks(user.id)
        emotion_count = user.emotion_history.count()
        
        stats.append({
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'total_tasks': task_counts['total'],
            'completed_tasks': task_counts['completed'],
            'emotion_entries': emotion_count
        })
    
    return stats


def get_overall_emotion_stats():
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
    emotions = Emotion.query.all()
    
    result = []
    for emotion in emotions:
        result.append(emotion.to_dict())
    
    return result


def get_emotion_by_id(emotion_id):
    emotion = db.session.get(Emotion, int(emotion_id))
    if emotion:
        return emotion.to_dict()
    return None


def get_emotion_by_name(emotion_name):
    emotion = Emotion.query.filter_by(name=emotion_name).first()
    if emotion:
        return emotion.to_dict()
    return None


# ==============================================
# Music Operations
# ==============================================

def get_all_music():
    music_list = Music.query.all()
    
    result = []
    for music in music_list:
        result.append(music.to_dict())
    
    return result


def get_music_by_emotion(emotion_name, limit):
    emotion = Emotion.query.filter_by(name=emotion_name).first()
    if not emotion:
        return []
    
    music_list = Music.query.filter_by(emotion_id=emotion.id).all()
    
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
    tags = BookTag.query.all()
    
    result = []
    for tag in tags:
        result.append(tag.to_dict())
    
    return result


def get_tag_by_slug(slug):
    tag = BookTag.query.filter_by(slug=slug).first()
    if tag:
        return tag.to_dict()
    return None


# ==============================================
# Book Operations
# ==============================================

def get_all_books():
    books = Book.query.all()
    
    result = []
    for book in books:
        result.append(book.to_dict())
    
    return result


def get_books_by_tags(tag_slugs, limit):
    if not tag_slugs:
        books = Book.query.all()
        result = []
        for book in books:
            result.append(book.to_dict())
        
        if limit and limit < len(result):
            return result[:limit]
        return result
    
    books = Book.query.all()
    result = []
    
    for book in books:
        book_tag_slugs = []
        for tag in book.tags:
            book_tag_slugs.append(tag.slug)
        
        match_count = 0
        for tag_slug in tag_slugs:
            if tag_slug in book_tag_slugs:
                match_count = match_count + 1
        
        if match_count == len(tag_slugs):
            result.append(book.to_dict())
    
    if limit and limit < len(result):
        return result[:limit]
    
    return result


# ==============================================
# Quote Operations
# ==============================================

def get_quotes_by_emotion(emotion_name):
    emotion = Emotion.query.filter_by(name=emotion_name).first()
    if not emotion:
        return []
    
    quotes = Quote.query.filter_by(emotion_id=emotion.id).all()
    
    result = []
    for quote in quotes:
        result.append(quote.to_dict())
    
    return result


def get_random_quote_by_emotion(emotion_name):
    emotion = Emotion.query.filter_by(name=emotion_name).first()
    if not emotion:
        return None
    
    quotes = Quote.query.filter_by(emotion_id=emotion.id).all()
    
    if len(quotes) == 0:
        return None
    
    random_index = random.randint(0, len(quotes) - 1)
    return quotes[random_index].to_dict()


def get_all_quotes():
    quotes = Quote.query.all()
    
    result = []
    for quote in quotes:
        result.append(quote.to_dict())
    
    return result
