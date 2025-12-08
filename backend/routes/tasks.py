# ==============================================
# Task Routes
# ==============================================

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime

import repository
import recommendation_engine

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('', methods=['GET'])
@login_required
def get_tasks():
    """Get all tasks for the current user."""
    user = current_user
    date_str = request.args.get('date')
    
    tasks = repository.get_tasks_by_user(user.id, date_str)
    
    return jsonify(tasks)


@tasks_bp.route('', methods=['POST'])
@login_required
def create_task():
    """Create a new task."""
    user = current_user
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    
    if data.get('task_date'):
        task_date = data['task_date']
    else:
        task_date = datetime.now().strftime('%Y-%m-%d')
    
    existing = repository.get_existing_task(
        user.id,
        data['title'],
        task_date
    )
    
    if existing:
        return jsonify({
            'error': 'Task already exists',
            'task': existing
        }), 409
    
    category = data.get('category', 'Personal')
    priority = data.get('priority', 'Medium')
    
    task = repository.create_task(
        user.id,
        data['title'],
        category,
        priority,
        task_date,
        data.get('recommended_for_emotion')
    )
    
    return jsonify(task), 201


@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    """Update a task."""
    user = current_user
    
    task = repository.get_task_by_id(task_id, user.id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    data = request.get_json()
    
    if 'is_completed' in data:
        task = repository.update_task(
            task_id,
            user.id,
            data['is_completed']
        )
    
    return jsonify(task)


@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    """Delete a task."""
    user = current_user
    
    success = repository.delete_task(task_id, user.id)
    
    if not success:
        return jsonify({'error': 'Task not found'}), 404
    
    return jsonify({'message': 'Task deleted'})


@tasks_bp.route('/recommended', methods=['GET'])
@login_required
def get_recommended_tasks():
    """Get recommended tasks based on current emotion."""
    user = current_user
    
    emotion = request.args.get('emotion')
    if not emotion:
        emotion = 'Neutral'
    
    limit = request.args.get('limit', 5, type=int)
    date_str = request.args.get('date')
    
    recommendations = recommendation_engine.get_recommended_tasks_from_repo(
        user.id,
        emotion,
        limit,
        date_str
    )
    
    return jsonify(recommendations)


@tasks_bp.route('/suggestions', methods=['GET'])
@login_required
def get_task_suggestions():
    """Get AI-suggested tasks based on current emotion."""
    emotion = request.args.get('emotion')
    if not emotion:
        emotion = 'Neutral'
    
    limit = request.args.get('limit', 3, type=int)
    
    suggestions = recommendation_engine.get_suggested_tasks(emotion, limit)
    
    return jsonify(suggestions)
