# ==============================================
# Music Routes
# ==============================================

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

import repository

music_bp = Blueprint('music', __name__)


@music_bp.route('/recommendations', methods=['GET'])
def get_music_recommendations():
    """Get music recommendations based on emotion."""
    emotion = request.args.get('emotion')
    if not emotion:
        emotion = 'Neutral'
    
    limit = request.args.get('limit', 4, type=int)
    
    music_list = repository.get_music_by_emotion(emotion, limit)
    
    return jsonify(music_list)


@music_bp.route('/all', methods=['GET'])
def get_all_music():
    """Get all music recommendations."""
    return jsonify(repository.get_all_music())


@music_bp.route('/favorites', methods=['GET'])
@login_required
def get_music_favorites():
    """Get all favorite music for the current user."""
    user = current_user
    favorite_ids = repository.get_user_music_favorites(user.id)
    
    all_music = repository.get_all_music()
    result = []
    for music_id in favorite_ids:
        for music in all_music:
            if music['id'] == music_id:
                music_copy = dict(music)
                music_copy['is_favorite'] = True
                result.append(music_copy)
                break
    
    return jsonify(result)


@music_bp.route('/favorites/ids', methods=['GET'])
@login_required
def get_music_favorite_ids():
    """Get list of favorite music IDs for the current user."""
    user = current_user
    favorite_ids = repository.get_user_music_favorites(user.id)
    return jsonify(favorite_ids)


@music_bp.route('/<int:music_id>/favorite', methods=['POST'])
@login_required
def add_music_to_favorites(music_id):
    """Add a music to favorites."""
    user = current_user
    success = repository.add_music_favorite(user.id, music_id)
    
    if success:
        return jsonify({'message': 'Added to favorites'})
    else:
        return jsonify({'message': 'Already in favorites'})


@music_bp.route('/<int:music_id>/favorite', methods=['DELETE'])
@login_required
def remove_music_from_favorites(music_id):
    """Remove a music from favorites."""
    user = current_user
    success = repository.remove_music_favorite(user.id, music_id)
    
    if success:
        return jsonify({'message': 'Removed from favorites'})
    else:
        return jsonify({'error': 'Not in favorites'}), 404
