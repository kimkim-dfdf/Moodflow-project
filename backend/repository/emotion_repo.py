# ==============================================
# Emotion Repository
# ==============================================
# Handles all emotion-related database operations
# ==============================================

from datetime import datetime
from models import db, EmotionHistory, Emotion


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
