# ==============================================
# MoodFlow - API Routes (Simplified)
# ==============================================
# This file contains all API endpoints
# All routes are registered with the Flask app
# ==============================================

from flask import request, jsonify, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import uuid

import repository
import recommendation_engine


# ==============================================
# Configuration
# ==============================================

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


# ==============================================
# Helper Functions
# ==============================================

def allowed_file(filename):
    """
    Check if a file extension is allowed for upload.
    Returns True if allowed, False otherwise.
    """
    if not filename:
        return False
    
    if '.' not in filename:
        return False
    
    parts = filename.rsplit('.', 1)
    extension = parts[1].lower()
    
    if extension in ALLOWED_EXTENSIONS:
        return True
    
    return False


# ==============================================
# Route Registration
# ==============================================

def register_routes(app):
    """
    Register all API routes with the Flask app.
    This function is called from app.py during initialization.
    """
    
    # ==========================================
    # Authentication Routes
    # ==========================================
    
    @app.route('/api/auth/login', methods=['POST'])
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
    
    
    @app.route('/api/auth/logout', methods=['POST'])
    @login_required
    def logout():
        """Log out the current user."""
        logout_user()
        return jsonify({'message': 'Logged out successfully'})
    
    
    @app.route('/api/auth/me', methods=['GET'])
    @login_required
    def get_current_user_route():
        """Get the currently logged in user's information."""
        return jsonify({'user': current_user.to_dict()})
    
    
    # ==========================================
    # Emotion Routes
    # ==========================================
    
    @app.route('/api/emotions', methods=['GET'])
    def get_emotions():
        """Get list of all available emotions."""
        return jsonify(repository.get_all_emotions())
    
    
    @app.route('/api/emotions/record', methods=['POST'])
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
    
    
    @app.route('/api/emotions/diary/<date_str>', methods=['GET'])
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
    
    
    @app.route('/api/emotions/statistics', methods=['GET'])
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
    
    
    # ==========================================
    # File Upload Routes
    # ==========================================
    
    @app.route('/api/upload/photo', methods=['POST'])
    @login_required
    def upload_photo():
        """Upload a photo for an emotion diary entry."""
        if 'photo' not in request.files:
            return jsonify({'error': 'No photo provided'}), 400
        
        file = request.files['photo']
        
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        filename = secure_filename(file.filename)
        unique_filename = uuid.uuid4().hex + '_' + filename
        
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        
        photo_url = '/api/uploads/' + unique_filename
        
        return jsonify({
            'photo_url': photo_url,
            'filename': unique_filename
        })
    
    
    @app.route('/api/uploads/<filename>')
    def serve_upload(filename):
        """Serve an uploaded file."""
        return send_from_directory(UPLOAD_FOLDER, filename)
    
    
    # ==========================================
    # Task Routes
    # ==========================================
    
    @app.route('/api/tasks', methods=['GET'])
    @login_required
    def get_tasks():
        """Get all tasks for the current user."""
        user = current_user
        date_str = request.args.get('date')
        
        tasks = repository.get_tasks_by_user(user.id, date_str)
        
        return jsonify(tasks)
    
    
    @app.route('/api/tasks', methods=['POST'])
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
    
    
    @app.route('/api/tasks/<int:task_id>', methods=['PUT'])
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
    
    
    @app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
    @login_required
    def delete_task(task_id):
        """Delete a task."""
        user = current_user
        
        success = repository.delete_task(task_id, user.id)
        
        if not success:
            return jsonify({'error': 'Task not found'}), 404
        
        return jsonify({'message': 'Task deleted'})
    
    
    @app.route('/api/tasks/recommended', methods=['GET'])
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
    
    
    @app.route('/api/tasks/suggestions', methods=['GET'])
    @login_required
    def get_task_suggestions():
        """Get AI-suggested tasks based on current emotion."""
        emotion = request.args.get('emotion')
        if not emotion:
            emotion = 'Neutral'
        
        limit = request.args.get('limit', 3, type=int)
        
        suggestions = recommendation_engine.get_suggested_tasks(emotion, limit)
        
        return jsonify(suggestions)
    
    
    # ==========================================
    # Music Routes
    # ==========================================
    
    @app.route('/api/music/recommendations', methods=['GET'])
    def get_music_recommendations():
        """Get music recommendations based on emotion."""
        emotion = request.args.get('emotion')
        if not emotion:
            emotion = 'Neutral'
        
        limit = request.args.get('limit', 4, type=int)
        
        music_list = repository.get_music_by_emotion(emotion, limit)
        
        return jsonify(music_list)
    
    
    @app.route('/api/music/all', methods=['GET'])
    def get_all_music():
        """Get all music recommendations."""
        return jsonify(repository.get_all_music())
    
    
    @app.route('/api/music/favorites', methods=['GET'])
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
    
    
    @app.route('/api/music/favorites/ids', methods=['GET'])
    @login_required
    def get_music_favorite_ids():
        """Get list of favorite music IDs for the current user."""
        user = current_user
        favorite_ids = repository.get_user_music_favorites(user.id)
        return jsonify(favorite_ids)
    
    
    @app.route('/api/music/<int:music_id>/favorite', methods=['POST'])
    @login_required
    def add_music_to_favorites(music_id):
        """Add a music to favorites."""
        user = current_user
        success = repository.add_music_favorite(user.id, music_id)
        
        if success:
            return jsonify({'message': 'Added to favorites'})
        else:
            return jsonify({'message': 'Already in favorites'})
    
    
    @app.route('/api/music/<int:music_id>/favorite', methods=['DELETE'])
    @login_required
    def remove_music_from_favorites(music_id):
        """Remove a music from favorites."""
        user = current_user
        success = repository.remove_music_favorite(user.id, music_id)
        
        if success:
            return jsonify({'message': 'Removed from favorites'})
        else:
            return jsonify({'error': 'Not in favorites'}), 404
    
    
    # ==========================================
    # Book Routes
    # ==========================================
    
    @app.route('/api/books/tags', methods=['GET'])
    def get_book_tags():
        """Get all book tags with their book counts."""
        tags = repository.get_all_book_tags()
        all_books = repository.get_all_books()
        
        result = []
        for tag in tags:
            tag_copy = dict(tag)
            
            count = 0
            for book in all_books:
                book_tag_slugs = []
                for t in book.get('tags', []):
                    if isinstance(t, dict):
                        book_tag_slugs.append(t.get('slug', ''))
                    else:
                        book_tag_slugs.append(t)
                
                if tag['slug'] in book_tag_slugs:
                    count = count + 1
            
            tag_copy['book_count'] = count
            result.append(tag_copy)
        
        for i in range(len(result)):
            for j in range(i + 1, len(result)):
                if result[j]['name'] < result[i]['name']:
                    temp = result[i]
                    result[i] = result[j]
                    result[j] = temp
        
        return jsonify(result)
    
    
    @app.route('/api/books', methods=['GET'])
    def get_books_by_tags():
        """Get books filtered by tags (AND logic)."""
        tag_slugs = request.args.getlist('tags')
        if not tag_slugs:
            tag_slugs = request.args.getlist('tags[]')
        
        limit = request.args.get('limit', 24, type=int)
        
        books = repository.get_books_by_tags(tag_slugs, limit)
        
        return jsonify(books)
    
    
    @app.route('/api/books/all', methods=['GET'])
    def get_all_books():
        """Get all book recommendations."""
        return jsonify(repository.get_all_books())
    
    
    @app.route('/api/books/search', methods=['GET'])
    def search_books():
        """Search books by title or author."""
        query = request.args.get('q', '')
        limit = request.args.get('limit', 24, type=int)
        
        if not query:
            return jsonify([])
        
        query_lower = query.lower()
        
        all_books = repository.get_all_books()
        result = []
        for book in all_books:
            title_lower = book['title'].lower()
            author_lower = book['author'].lower()
            
            title_match = query_lower in title_lower
            author_match = query_lower in author_lower
            
            if title_match or author_match:
                result.append(book)
        
        if len(result) > limit:
            result = result[:limit]
        
        return jsonify(result)
    
    
    # ==========================================
    # Book Favorites Routes
    # ==========================================
    
    @app.route('/api/books/favorites', methods=['GET'])
    @login_required
    def get_favorites():
        """Get all favorite books for the current user."""
        user = current_user
        favorite_ids = repository.get_user_book_favorites(user.id)
        
        all_books = repository.get_all_books()
        result = []
        for book_id in favorite_ids:
            for book in all_books:
                if book['id'] == book_id:
                    book_copy = dict(book)
                    book_copy['is_favorite'] = True
                    result.append(book_copy)
                    break
        
        return jsonify(result)
    
    
    @app.route('/api/books/favorites/ids', methods=['GET'])
    @login_required
    def get_favorite_ids():
        """Get list of favorite book IDs for the current user."""
        user = current_user
        favorite_ids = repository.get_user_book_favorites(user.id)
        return jsonify(favorite_ids)
    
    
    @app.route('/api/books/<int:book_id>/favorite', methods=['POST'])
    @login_required
    def add_to_favorites(book_id):
        """Add a book to favorites."""
        user = current_user
        success = repository.add_book_favorite(user.id, book_id)
        
        if success:
            return jsonify({'message': 'Added to favorites'})
        else:
            return jsonify({'message': 'Already in favorites'})
    
    
    @app.route('/api/books/<int:book_id>/favorite', methods=['DELETE'])
    @login_required
    def remove_from_favorites(book_id):
        """Remove a book from favorites."""
        user = current_user
        success = repository.remove_book_favorite(user.id, book_id)
        
        if success:
            return jsonify({'message': 'Removed from favorites'})
        else:
            return jsonify({'error': 'Not in favorites'}), 404
    
    
    # ==========================================
    # Profile Routes
    # ==========================================
    
    @app.route('/api/user/profile', methods=['PUT'])
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
    
    
    # ==========================================
    # Admin Routes
    # ==========================================
    
    def admin_required(f):
        """Decorator to require admin access."""
        from functools import wraps
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'Login required'}), 401
            if not current_user.is_admin:
                return jsonify({'error': 'Admin access required'}), 403
            return f(*args, **kwargs)
        return decorated_function
    
    @app.route('/api/admin/stats', methods=['GET'])
    @admin_required
    def get_admin_stats():
        """Get overall statistics for admin dashboard."""
        user_stats = repository.get_all_users_stats()
        emotion_stats = repository.get_overall_emotion_stats()
        task_stats = repository.get_overall_task_stats()
        
        emotion_details = []
        for emotion_id, count in emotion_stats.items():
            emotion = repository.get_emotion_by_id(int(emotion_id))
            if emotion:
                emotion_details.append({
                    'emotion': emotion,
                    'count': count
                })
        
        return jsonify({
            'users': user_stats,
            'emotions': emotion_details,
            'tasks': task_stats,
            'total_users': len(user_stats)
        })
    
    
    @app.route('/api/admin/music', methods=['GET'])
    @admin_required
    def get_all_music_admin():
        """Get all music for admin."""
        return jsonify(repository.get_all_music())
    
    
    @app.route('/api/admin/books', methods=['GET'])
    @admin_required
    def get_all_books_admin():
        """Get all books for admin."""
        return jsonify(repository.get_all_books())
    
    
    @app.route('/api/admin/tags', methods=['GET'])
    @admin_required
    def get_all_tags_admin():
        """Get all book tags for admin."""
        return jsonify(repository.get_all_book_tags())
    
    
    # ==========================================
    # Dashboard Routes
    # ==========================================
    
    @app.route('/api/dashboard/summary', methods=['GET'])
    @login_required
    def get_dashboard_summary():
        """Get a summary of data for the dashboard."""
        user = current_user
        today = datetime.now().strftime('%Y-%m-%d')
        
        today_emotion = repository.get_emotion_entry_by_date(user.id, today)
        
        task_counts = repository.count_tasks(user.id)
        total_tasks = task_counts['total']
        completed_tasks = task_counts['completed']
        pending_tasks = total_tasks - completed_tasks
        
        today_tasks = repository.get_today_due_tasks(user.id, today)
        
        emotion_stats = recommendation_engine.get_emotion_statistics_from_repo(
            user.id,
            7
        )
        
        today_emotion_dict = None
        if today_emotion:
            emotion = repository.get_emotion_by_id(today_emotion['emotion_id'])
            today_emotion_dict = dict(today_emotion)
            today_emotion_dict['emotion'] = emotion
        
        return jsonify({
            'user': repository.user_to_dict(user),
            'today_emotion': today_emotion_dict,
            'task_summary': {
                'total': total_tasks,
                'completed': completed_tasks,
                'pending': pending_tasks
            },
            'today_tasks': today_tasks,
            'weekly_mood_stats': emotion_stats
        })
