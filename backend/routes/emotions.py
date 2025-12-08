# ==============================================
# Emotion Routes
# ==============================================

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime

import repository
import recommendation_engine

emotions_bp = Blueprint('emotions', __name__)


@emotions_bp.route('', methods=['GET'])
def get_emotions():
    """Get list of all available emotions."""
    return jsonify(repository.get_all_emotions())


@emotions_bp.route('/record', methods=['POST'])
@login_required
def record_emotion():
    """Record an emotion for a specific date."""
    data = request.get_json()
    user = current_user
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if not data.get('emotion_id'):
        return jsonify({'error': 'Emotion ID is required'}), 400
    
    if data.get('date'):
        date = data['date']
    else:
        date = datetime.now().strftime('%Y-%m-%d')
    
    entry = repository.create_emotion_entry(
        user.id,
        data['emotion_id'],
        date,
        data.get('notes'),
        data.get('photo_url')
    )
    
    emotion = repository.get_emotion_by_id(entry['emotion_id'])
    entry_dict = dict(entry)
    entry_dict['emotion'] = emotion
    
    return jsonify({
        'message': 'Emotion recorded',
        'entry': entry_dict
    })


@emotions_bp.route('/diary/<date_str>', methods=['GET'])
@login_required
def get_diary_entry(date_str):
    """Get the emotion diary entry for a specific date."""
    user = current_user
    entry = repository.get_emotion_entry_by_date(user.id, date_str)
    
    if entry:
        emotion = repository.get_emotion_by_id(entry['emotion_id'])
        entry_dict = dict(entry)
        entry_dict['emotion'] = emotion
        return jsonify(entry_dict)
    
    return jsonify(None)


@emotions_bp.route('/statistics', methods=['GET'])
@login_required
def get_emotion_statistics():
    """Get emotion statistics for the current user."""
    user = current_user
    days = request.args.get('days', 30, type=int)
    
    stats = recommendation_engine.get_emotion_statistics_from_repo(
        user.id,
        days
    )
    
    return jsonify(stats)
