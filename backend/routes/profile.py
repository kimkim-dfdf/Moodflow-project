# ==============================================
# Profile Routes
# ==============================================

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

import repository

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """Update the current user's profile."""
    user = current_user
    data = request.get_json()
    
    if 'username' in data:
        existing = repository.get_user_by_username(data['username'])
        if existing and existing.id != user.id:
            return jsonify({'error': 'Username already taken'}), 400
        
        user = repository.update_user(user.id, data['username'])
    
    return jsonify(repository.user_to_dict(user))
