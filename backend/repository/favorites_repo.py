# ==============================================
# Favorites Repository
# ==============================================
# Handles book and music favorites operations
# ==============================================

from datetime import datetime
from models import db, BookFavorite, MusicFavorite


# ==============================================
# Book Favorites
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
# Music Favorites
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
