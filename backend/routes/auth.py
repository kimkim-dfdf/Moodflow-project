# ==============================================
# Authentication Routes
# ==============================================

from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user

import repository

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """Log in with a demo account."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if not data.get('email'):
        return jsonify({'error': 'Email is required'}), 400
    
    if not data.get('password'):
        return jsonify({'error': 'Password is required'}), 400
    
    user = repository.get_user_by_email(data['email'])
    
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    password_correct = repository.check_user_password(user, data['password'])
    if not password_correct:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    login_user(user)
    
    return jsonify({
        'message': 'Login successful',
        'user': repository.user_to_dict(user)
    })


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Log out the current user."""
    logout_user()
    return jsonify({'message': 'Logged out successfully'})


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Get the currently logged in user's information."""
    return jsonify({'user': current_user.to_dict()})
