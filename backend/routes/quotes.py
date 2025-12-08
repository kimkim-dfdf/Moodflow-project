# ==============================================
# MoodFlow - Quotes Routes
# ==============================================

from flask import Blueprint, request, jsonify
from flask_login import login_required
import repository

quotes_bp = Blueprint('quotes', __name__)


@quotes_bp.route('/random', methods=['GET'])
@login_required
def get_random_quote():
    """
    Get a random quote for a specific emotion.
    Query parameter: emotion (required)
    Returns one random quote matching the emotion.
    """
    emotion = request.args.get('emotion')
    
    if not emotion:
        return jsonify({'error': 'Emotion parameter is required'}), 400
    
    quote = repository.get_random_quote_by_emotion(emotion)
    
    if quote is None:
        return jsonify({'error': 'No quotes found for this emotion'}), 404
    
    return jsonify(quote)


@quotes_bp.route('/', methods=['GET'])
@login_required
def get_quotes():
    """
    Get all quotes or filter by emotion.
    Query parameter: emotion (optional)
    Returns list of quotes.
    """
    emotion = request.args.get('emotion')
    
    if emotion:
        quotes = repository.get_quotes_by_emotion(emotion)
    else:
        quotes = repository.get_all_quotes()
    
    return jsonify(quotes)
