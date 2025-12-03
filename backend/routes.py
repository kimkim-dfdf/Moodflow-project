# ==============================================
# MoodFlow - API Routes
# ==============================================
# This file contains all API endpoints
# All routes are registered with the Flask app
# ==============================================

from flask import request, jsonify, session, send_from_directory
from datetime import datetime
from functools import wraps
import os
import uuid

import repository
import recommendation_engine
import static_data


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
    
    # Get the file extension
    parts = filename.rsplit('.', 1)
    extension = parts[1].lower()
    
    if extension in ALLOWED_EXTENSIONS:
        return True
    
    return False


def login_required(f):
    """
    Decorator to require login for a route.
    Returns 401 error if user is not logged in.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Login required'}), 401
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """
    Get the currently logged in user.
    Returns None if not logged in.
    """
    if 'user_id' not in session:
        return None
    
    return repository.get_user_by_id(session['user_id'])


# ==============================================
# Route Registration
# ==============================================

def register_routes(app):
    """
    Register all API routes with the Flask app.
    This function is called from app.py during initialization.
    """
    
    # ==========================================
    # Authentication Routes (Simplified for Demo)
    # ==========================================
    # Only 3 demo accounts can log in:
    # - seven@gmail.com
    # - elly@gmail.com
    # - nicole@gmail.com
    # Password for all: ekdus123
    # ==========================================
    
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        """
        Registration is disabled for demo.
        Only pre-defined demo accounts can log in.
        """
        return jsonify({
            'error': 'Registration is disabled. Please use a demo account.'
        }), 400
    
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """
        Log in with a demo account.
        Only 3 accounts are available.
        """
        data = request.get_json()
        
        # Check if data was provided
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Check if email was provided
        if not data.get('email'):
            return jsonify({'error': 'Email is required'}), 400
        
        # Check if password was provided
        if not data.get('password'):
            return jsonify({'error': 'Password is required'}), 400
        
        # Find user by email
        user = repository.get_user_by_email(data['email'])
        
        # Check if user exists
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check if password is correct
        password_correct = repository.check_user_password(user, data['password'])
        if not password_correct:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Log user in by saving user_id to session
        session['user_id'] = user['id']
        
        return jsonify({
            'message': 'Login successful',
            'user': repository.user_to_dict(user)
        })
    
    
    @app.route('/api/auth/logout', methods=['POST'])
    @login_required
    def logout():
        """Log out the current user."""
        session.pop('user_id', None)
        return jsonify({'message': 'Logged out successfully'})
    
    
    @app.route('/api/auth/me', methods=['GET'])
    @login_required
    def get_current_user_route():
        """Get the currently logged in user's information."""
        user = get_current_user()
        return jsonify({'user': repository.user_to_dict(user)})
    
    
    # ==========================================
    # Emotion Routes
    # ==========================================
    
    @app.route('/api/emotions', methods=['GET'])
    def get_emotions():
        """Get list of all available emotions."""
        return jsonify(static_data.EMOTIONS)
    
    
    @app.route('/api/emotions/record', methods=['POST'])
    @login_required
    def record_emotion():
        """
        Record an emotion for a specific date.
        Required fields: emotion_id
        Optional fields: date, notes, photo_url
        """
        data = request.get_json()
        user = get_current_user()
        
        # Validate input
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        if not data.get('emotion_id'):
            return jsonify({'error': 'Emotion ID is required'}), 400
        
        # Get date (default to today)
        if data.get('date'):
            date = data['date']
        else:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # Create emotion entry
        entry = repository.create_emotion_entry(
            user['id'],
            data['emotion_id'],
            date,
            data.get('notes'),
            data.get('photo_url')
        )
        
        # Add emotion details to response
        emotion = static_data.get_emotion_by_id(entry['emotion_id'])
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
        user = get_current_user()
        entry = repository.get_emotion_entry_by_date(user['id'], date_str)
        
        if entry:
            emotion = static_data.get_emotion_by_id(entry['emotion_id'])
            entry_dict = dict(entry)
            entry_dict['emotion'] = emotion
            return jsonify(entry_dict)
        
        return jsonify(None)
    
    
    @app.route('/api/emotions/statistics', methods=['GET'])
    @login_required
    def get_emotion_statistics():
        """
        Get emotion statistics for the current user.
        Optional query param: days (default 30)
        """
        user = get_current_user()
        days = request.args.get('days', 30, type=int)
        
        stats = recommendation_engine.get_emotion_statistics_from_repo(
            user['id'],
            days
        )
        
        return jsonify(stats)
    
    
    # ==========================================
    # File Upload Routes
    # ==========================================
    
    @app.route('/api/upload/photo', methods=['POST'])
    @login_required
    def upload_photo():
        """
        Upload a photo for an emotion diary entry.
        Requires a 'photo' file in the request.
        """
        # Check if file was uploaded
        if 'photo' not in request.files:
            return jsonify({'error': 'No photo provided'}), 400
        
        file = request.files['photo']
        
        # Check if filename is empty
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Create unique filename
        filename = secure_filename(file.filename)
        unique_filename = uuid.uuid4().hex + '_' + filename
        
        # Create upload folder if it doesn't exist
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        
        # Save file
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        
        # Return URL to access the file
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
        """
        Get all tasks for the current user.
        Optional query param: date (filter by task_date)
        """
        user = get_current_user()
        date_str = request.args.get('date')
        
        tasks = repository.get_tasks_by_user(user['id'], date_str)
        
        return jsonify(tasks)
    
    
    @app.route('/api/tasks', methods=['POST'])
    @login_required
    def create_task():
        """
        Create a new task.
        Required fields: title
        Optional fields: category, priority, task_date, recommended_for_emotion
        """
        user = get_current_user()
        data = request.get_json()
        
        # Validate input
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        if not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400
        
        # Get task date (default to today)
        if data.get('task_date'):
            task_date = data['task_date']
        else:
            task_date = datetime.now().strftime('%Y-%m-%d')
        
        # Check for duplicate task
        existing = repository.get_existing_task(
            user['id'],
            data['title'],
            task_date
        )
        
        if existing:
            return jsonify({
                'error': 'Task already exists',
                'task': existing
            }), 409
        
        # Set defaults
        category = data.get('category', 'Personal')
        priority = data.get('priority', 'Medium')
        
        # Create task
        task = repository.create_task(
            user['id'],
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
        """
        Update a task.
        Currently supports updating: is_completed
        """
        user = get_current_user()
        
        # Find the task
        task = repository.get_task_by_id(task_id, user['id'])
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        data = request.get_json()
        
        # Update completion status
        if 'is_completed' in data:
            task = repository.update_task(
                task_id,
                user['id'],
                data['is_completed']
            )
        
        return jsonify(task)
    
    
    @app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
    @login_required
    def delete_task(task_id):
        """Delete a task."""
        user = get_current_user()
        
        success = repository.delete_task(task_id, user['id'])
        
        if not success:
            return jsonify({'error': 'Task not found'}), 404
        
        return jsonify({'message': 'Task deleted'})
    
    
    @app.route('/api/tasks/recommended', methods=['GET'])
    @login_required
    def get_recommended_tasks():
        """
        Get recommended tasks based on current emotion.
        Query params: emotion, limit (default 5), date
        """
        user = get_current_user()
        
        # Get parameters
        emotion = request.args.get('emotion')
        if not emotion:
            emotion = 'Neutral'
        
        limit = request.args.get('limit', 5, type=int)
        date_str = request.args.get('date')
        
        # Get recommendations
        recommendations = recommendation_engine.get_recommended_tasks_from_repo(
            user['id'],
            emotion,
            limit,
            date_str
        )
        
        return jsonify(recommendations)
    
    
    @app.route('/api/tasks/suggestions', methods=['GET'])
    @login_required
    def get_task_suggestions():
        """
        Get AI-suggested tasks based on current emotion.
        Query params: emotion, limit (default 3)
        """
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
        """
        Get music recommendations based on emotion.
        Query params: emotion, limit (default 4)
        """
        emotion = request.args.get('emotion')
        if not emotion:
            emotion = 'Neutral'
        
        limit = request.args.get('limit', 4, type=int)
        
        recommendations = static_data.get_music_by_emotion(emotion, limit)
        
        return jsonify(recommendations)
    
    
    # ==========================================
    # Book Routes
    # ==========================================
    
    @app.route('/api/books/tags', methods=['GET'])
    def get_book_tags():
        """
        Get all book tags with their book counts.
        Tags are sorted alphabetically by name.
        """
        tags = static_data.get_all_book_tags()
        
        # Add book count for each tag
        result = []
        for tag in tags:
            tag_copy = dict(tag)
            
            # Count books with this tag
            count = 0
            for book in static_data.BOOK_RECOMMENDATIONS:
                if tag['slug'] in book['tags']:
                    count = count + 1
            
            tag_copy['book_count'] = count
            result.append(tag_copy)
        
        # Sort alphabetically using bubble sort
        for i in range(len(result)):
            for j in range(i + 1, len(result)):
                if result[j]['name'] < result[i]['name']:
                    temp = result[i]
                    result[i] = result[j]
                    result[j] = temp
        
        return jsonify(result)
    
    
    @app.route('/api/books', methods=['GET'])
    def get_books_by_tags():
        """
        Get books filtered by tags (AND logic).
        Query params: tags (array), limit (default 24)
        """
        # Get tags from query parameters
        tag_slugs = request.args.getlist('tags')
        if not tag_slugs:
            tag_slugs = request.args.getlist('tags[]')
        
        limit = request.args.get('limit', 24, type=int)
        
        # Get books matching tags
        books = static_data.get_books_by_tags(tag_slugs, limit)
        
        # Add full tag objects to each book
        result = []
        for book in books:
            book_copy = dict(book)
            book_copy['tags'] = static_data.get_tag_objects_for_book(book)
            result.append(book_copy)
        
        return jsonify(result)
    
    
    # ==========================================
    # Profile Routes
    # ==========================================
    
    @app.route('/api/user/profile', methods=['PUT'])
    @login_required
    def update_profile():
        """
        Update the current user's profile.
        Supports updating: username
        """
        user = get_current_user()
        data = request.get_json()
        
        if 'username' in data:
            # Check if username is taken
            existing = repository.get_user_by_username(data['username'])
            if existing and existing['id'] != user['id']:
                return jsonify({'error': 'Username already taken'}), 400
            
            # Update username
            user = repository.update_user(user['id'], data['username'])
        
        return jsonify(repository.user_to_dict(user))
    
    
    # ==========================================
    # Dashboard Routes
    # ==========================================
    
    @app.route('/api/dashboard/summary', methods=['GET'])
    @login_required
    def get_dashboard_summary():
        """
        Get a summary of data for the dashboard.
        Includes: user info, today's emotion, task counts, weekly stats
        """
        user = get_current_user()
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Get today's emotion
        today_emotion = repository.get_emotion_entry_by_date(user['id'], today)
        
        # Get task counts
        task_counts = repository.count_tasks(user['id'])
        total_tasks = task_counts['total']
        completed_tasks = task_counts['completed']
        pending_tasks = total_tasks - completed_tasks
        
        # Get tasks due today
        today_tasks = repository.get_today_due_tasks(user['id'], today)
        
        # Get weekly emotion statistics
        emotion_stats = recommendation_engine.get_emotion_statistics_from_repo(
            user['id'],
            7
        )
        
        # Format today's emotion for response
        today_emotion_dict = None
        if today_emotion:
            emotion = static_data.get_emotion_by_id(today_emotion['emotion_id'])
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
