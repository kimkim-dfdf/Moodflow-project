# ==============================================
# Music Repository
# ==============================================
# Handles all music-related database operations
# ==============================================

from models import Music


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
