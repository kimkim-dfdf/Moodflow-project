# ==============================================
# MoodFlow - API Routes
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
import hashlib

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
        
        # Log user in using Flask-Login
        login_user(user)
        
        return jsonify({
            'message': 'Login successful',
            'user': repository.user_to_dict(user)
        })
    
    
    @app.route('/api/auth/logout', methods=['POST'])
    @login_required
    def logout():
        """Log out the current user using Flask-Login."""
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
        user = current_user
        
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
            user.id,
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
        user = current_user
        entry = repository.get_emotion_entry_by_date(user.id, date_str)
        
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
        user = current_user
        date_str = request.args.get('date')
        
        tasks = repository.get_tasks_by_user(user.id, date_str)
        
        return jsonify(tasks)
    
    
    @app.route('/api/tasks', methods=['POST'])
    @login_required
    def create_task():
        """
        Create a new task.
        Required fields: title
        Optional fields: category, priority, task_date, recommended_for_emotion
        """
        user = current_user
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
            user.id,
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
        """
        Update a task.
        Currently supports updating: is_completed
        """
        user = current_user
        
        # Find the task
        task = repository.get_task_by_id(task_id, user.id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        data = request.get_json()
        
        # Update completion status
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
        """
        Get recommended tasks based on current emotion.
        Query params: emotion, limit (default 5), date
        """
        user = current_user
        
        # Get parameters
        emotion = request.args.get('emotion')
        if not emotion:
            emotion = 'Neutral'
        
        limit = request.args.get('limit', 5, type=int)
        date_str = request.args.get('date')
        
        # Get recommendations
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
        Includes both static music and custom music added by admin.
        """
        emotion = request.args.get('emotion')
        if not emotion:
            emotion = 'Neutral'
        
        limit = request.args.get('limit', 4, type=int)
        
        # Get custom music from repository first
        custom_music = repository.get_all_custom_music()
        
        # Filter custom music by emotion
        filtered_custom = []
        for music in custom_music:
            if music.get('emotion') == emotion:
                filtered_custom.append(music)
        
        # Get static music recommendations
        static_music = static_data.get_music_by_emotion(emotion, limit)
        
        # Combine: custom music first, then static music
        all_music = filtered_custom + list(static_music)
        
        # Limit results
        if len(all_music) > limit:
            all_music = all_music[:limit]
        
        return jsonify(all_music)
    
    
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
        Includes both static books and custom books added by admin.
        """
        # Get tags from query parameters
        tag_slugs = request.args.getlist('tags')
        if not tag_slugs:
            tag_slugs = request.args.getlist('tags[]')
        
        limit = request.args.get('limit', 24, type=int)
        
        # Get custom books from repository first
        custom_books = repository.get_all_custom_books()
        
        # Filter custom books by tags if tags are specified
        filtered_custom = []
        for book in custom_books:
            if not tag_slugs:
                filtered_custom.append(book)
            else:
                has_all_tags = True
                for tag in tag_slugs:
                    if tag not in book.get('tags', []):
                        has_all_tags = False
                        break
                if has_all_tags:
                    filtered_custom.append(book)
        
        # Get static books matching tags
        static_books = static_data.get_books_by_tags(tag_slugs, limit)
        
        # Combine: custom books first, then static books
        all_books = filtered_custom + list(static_books)
        
        # Limit results
        if len(all_books) > limit:
            all_books = all_books[:limit]
        
        # Add full tag objects to each book
        result = []
        for book in all_books:
            book_copy = dict(book)
            book_copy['tags'] = static_data.get_tag_objects_for_book(book)
            result.append(book_copy)
        
        return jsonify(result)
    
    
    @app.route('/api/books/search', methods=['GET'])
    def search_books():
        """
        Search books by title or author.
        Query params: q (search query), limit (default 24)
        """
        query = request.args.get('q', '')
        limit = request.args.get('limit', 24, type=int)
        
        if not query:
            return jsonify([])
        
        # Convert query to lowercase for case-insensitive search
        query_lower = query.lower()
        
        # Search in static books
        result = []
        for book in static_data.BOOK_RECOMMENDATIONS:
            title_lower = book['title'].lower()
            author_lower = book['author'].lower()
            
            # Check if query matches title or author
            title_match = query_lower in title_lower
            author_match = query_lower in author_lower
            
            if title_match or author_match:
                book_copy = dict(book)
                book_copy['tags'] = static_data.get_tag_objects_for_book(book)
                result.append(book_copy)
        
        # Search in custom books
        custom_books = repository.get_all_custom_books()
        for book in custom_books:
            title_lower = book['title'].lower()
            author_lower = book.get('author', '').lower()
            
            title_match = query_lower in title_lower
            author_match = query_lower in author_lower
            
            if title_match or author_match:
                book_copy = dict(book)
                book_copy['tags'] = static_data.get_tag_objects_for_book(book)
                result.append(book_copy)
        
        # Limit results
        if len(result) > limit:
            result = result[:limit]
        
        return jsonify(result)
    
    
    # ==========================================
    # Book Favorites Routes
    # ==========================================
    
    @app.route('/api/books/favorites', methods=['GET'])
    @login_required
    def get_favorites():
        """
        Get all favorite books for the current user.
        """
        user = current_user
        favorite_ids = repository.get_user_favorites(user.id)
        
        # Get full book details for each favorite
        result = []
        for book_id in favorite_ids:
            # Search in static books
            found = False
            for book in static_data.BOOK_RECOMMENDATIONS:
                if book['id'] == book_id:
                    book_copy = dict(book)
                    book_copy['tags'] = static_data.get_tag_objects_for_book(book)
                    book_copy['is_favorite'] = True
                    result.append(book_copy)
                    found = True
                    break
            
            # Search in custom books if not found
            if not found:
                custom_books = repository.get_all_custom_books()
                for book in custom_books:
                    if book['id'] == book_id:
                        book_copy = dict(book)
                        book_copy['tags'] = static_data.get_tag_objects_for_book(book)
                        book_copy['is_favorite'] = True
                        result.append(book_copy)
                        break
        
        return jsonify(result)
    
    
    @app.route('/api/books/favorites/ids', methods=['GET'])
    @login_required
    def get_favorite_ids():
        """
        Get list of favorite book IDs for the current user.
        """
        user = current_user
        favorite_ids = repository.get_user_favorites(user.id)
        return jsonify(favorite_ids)
    
    
    @app.route('/api/books/<int:book_id>/favorite', methods=['POST'])
    @login_required
    def add_to_favorites(book_id):
        """
        Add a book to favorites.
        """
        user = current_user
        success = repository.add_favorite(user.id, book_id)
        
        if success:
            return jsonify({'message': 'Added to favorites'})
        else:
            return jsonify({'message': 'Already in favorites'})
    
    
    @app.route('/api/books/<int:book_id>/favorite', methods=['DELETE'])
    @login_required
    def remove_from_favorites(book_id):
        """
        Remove a book from favorites.
        """
        user = current_user
        success = repository.remove_favorite(user.id, book_id)
        
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
        """
        Update the current user's profile.
        Supports updating: username
        """
        user = current_user
        data = request.get_json()
        
        if 'username' in data:
            # Check if username is taken
            existing = repository.get_user_by_username(data['username'])
            if existing and existing.id != user.id:
                return jsonify({'error': 'Username already taken'}), 400
            
            # Update username
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
            emotion = static_data.get_emotion_by_id(int(emotion_id))
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
    def get_all_music():
        """Get all music (static + custom)."""
        all_music = []
        for m in static_data.MUSIC_RECOMMENDATIONS:
            music_copy = dict(m)
            music_copy['is_custom'] = False
            all_music.append(music_copy)
        custom = repository.get_all_custom_music()
        for m in custom:
            all_music.append(m)
        return jsonify(all_music)
    
    @app.route('/api/admin/music', methods=['POST'])
    @admin_required
    def create_music():
        """Create a new music recommendation."""
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        if not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400
        if not data.get('emotion'):
            return jsonify({'error': 'Emotion is required'}), 400
        
        music = repository.create_music(
            data['emotion'],
            data['title'],
            data.get('artist', ''),
            data.get('genre', ''),
            data.get('youtube_url', '')
        )
        
        return jsonify(music), 201
    
    @app.route('/api/admin/music/<int:music_id>', methods=['PUT'])
    @admin_required
    def update_music(music_id):
        """Update a custom music entry."""
        data = request.get_json()
        
        music = repository.update_music(
            music_id,
            data.get('emotion'),
            data.get('title'),
            data.get('artist'),
            data.get('genre'),
            data.get('youtube_url')
        )
        
        if not music:
            return jsonify({'error': 'Music not found or is static'}), 404
        
        return jsonify(music)
    
    @app.route('/api/admin/music/<int:music_id>', methods=['DELETE'])
    @admin_required
    def delete_music(music_id):
        """Delete a custom music entry."""
        success = repository.delete_music(music_id)
        
        if not success:
            return jsonify({'error': 'Music not found or is static'}), 404
        
        return jsonify({'message': 'Music deleted'})
    
    @app.route('/api/admin/books', methods=['GET'])
    @admin_required
    def get_all_books_admin():
        """Get all books (static + custom) for admin."""
        all_books = []
        for b in static_data.BOOK_RECOMMENDATIONS:
            book_copy = dict(b)
            book_copy['is_custom'] = False
            all_books.append(book_copy)
        custom = repository.get_all_custom_books()
        for b in custom:
            all_books.append(b)
        return jsonify(all_books)
    
    @app.route('/api/admin/books', methods=['POST'])
    @admin_required
    def create_book():
        """Create a new book recommendation."""
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        if not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400
        
        book = repository.create_book(
            data.get('emotion', 'Neutral'),
            data['title'],
            data.get('author', ''),
            data.get('genre', ''),
            data.get('description', ''),
            data.get('tags', [])
        )
        
        return jsonify(book), 201
    
    @app.route('/api/admin/books/<int:book_id>', methods=['PUT'])
    @admin_required
    def update_book(book_id):
        """Update a custom book entry."""
        data = request.get_json()
        
        book = repository.update_book(
            book_id,
            data.get('emotion'),
            data.get('title'),
            data.get('author'),
            data.get('genre'),
            data.get('description'),
            data.get('tags', [])
        )
        
        if not book:
            return jsonify({'error': 'Book not found or is static'}), 404
        
        return jsonify(book)
    
    @app.route('/api/admin/books/<int:book_id>', methods=['DELETE'])
    @admin_required
    def delete_book(book_id):
        """Delete a custom book entry."""
        success = repository.delete_book(book_id)
        
        if not success:
            return jsonify({'error': 'Book not found or is static'}), 404
        
        return jsonify({'message': 'Book deleted'})
    
    @app.route('/api/admin/tags', methods=['GET'])
    @admin_required
    def get_all_tags_admin():
        """Get all book tags for admin including custom book tags."""
        all_tags = []
        existing_slugs = set()
        
        for tag in static_data.BOOK_TAGS:
            all_tags.append(dict(tag))
            existing_slugs.add(tag['slug'])
        
        custom_books = repository.get_all_custom_books()
        for book in custom_books:
            for tag_slug in book.get('tags', []):
                if tag_slug not in existing_slugs:
                    hash_digest = hashlib.md5(tag_slug.encode()).hexdigest()
                    stable_id = 1000 + int(hash_digest[:8], 16) % 9000
                    all_tags.append({
                        'id': stable_id,
                        'slug': tag_slug,
                        'name': tag_slug.replace('-', ' ').title(),
                        'color': '#6B7280'
                    })
                    existing_slugs.add(tag_slug)
        
        return jsonify(all_tags)
    
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
        user = current_user
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Get today's emotion
        today_emotion = repository.get_emotion_entry_by_date(user.id, today)
        
        # Get task counts
        task_counts = repository.count_tasks(user.id)
        total_tasks = task_counts['total']
        completed_tasks = task_counts['completed']
        pending_tasks = total_tasks - completed_tasks
        
        # Get tasks due today
        today_tasks = repository.get_today_due_tasks(user.id, today)
        
        # Get weekly emotion statistics
        emotion_stats = recommendation_engine.get_emotion_statistics_from_repo(
            user.id,
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
