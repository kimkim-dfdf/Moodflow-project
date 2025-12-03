from flask import request, jsonify, session, send_from_directory
from datetime import datetime, timedelta
from functools import wraps
from werkzeug.utils import secure_filename
import repository
import recommendation_engine
import static_data
import os
import uuid


UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    if not filename:
        return False
    if '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    if ext in ALLOWED_EXTENSIONS:
        return True
    return False


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Login required'}), 401
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    if 'user_id' not in session:
        return None
    return repository.get_user_by_id(session['user_id'])


def register_routes(app):
    
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        if not data.get('email'):
            return jsonify({'error': 'Email is required'}), 400
        if not data.get('password'):
            return jsonify({'error': 'Password is required'}), 400
        if not data.get('username'):
            return jsonify({'error': 'Username is required'}), 400
        
        existing_email = repository.get_user_by_email(data['email'])
        if existing_email:
            return jsonify({'error': 'Email already registered'}), 400
        
        existing_username = repository.get_user_by_username(data['username'])
        if existing_username:
            return jsonify({'error': 'Username already taken'}), 400
        
        user = repository.create_user(data['email'], data['username'], data['password'])
        session['user_id'] = user['id']
        
        return jsonify({'message': 'Registration successful', 'user': repository.user_to_dict(user)}), 201
    
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
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
        if not repository.check_user_password(user, data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        session['user_id'] = user['id']
        return jsonify({'message': 'Login successful', 'user': repository.user_to_dict(user)})
    
    
    @app.route('/api/auth/logout', methods=['POST'])
    @login_required
    def logout():
        session.pop('user_id', None)
        return jsonify({'message': 'Logged out successfully'})
    
    
    @app.route('/api/auth/me', methods=['GET'])
    @login_required
    def get_current_user_route():
        user = get_current_user()
        return jsonify({'user': repository.user_to_dict(user)})
    
    
    @app.route('/api/emotions', methods=['GET'])
    def get_emotions():
        return jsonify(static_data.EMOTIONS)
    
    
    @app.route('/api/emotions/record', methods=['POST'])
    @login_required
    def record_emotion():
        data = request.get_json()
        user = get_current_user()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        if not data.get('emotion_id'):
            return jsonify({'error': 'Emotion ID is required'}), 400
        
        if data.get('date'):
            date = data['date']
        else:
            date = datetime.now().strftime('%Y-%m-%d')
        
        entry = repository.create_emotion_entry(
            user['id'],
            data['emotion_id'],
            date,
            data.get('notes'),
            data.get('photo_url')
        )
        
        emotion = static_data.get_emotion_by_id(entry['emotion_id'])
        entry_dict = dict(entry)
        entry_dict['emotion'] = emotion
        
        return jsonify({'message': 'Emotion recorded', 'entry': entry_dict})
    
    
    @app.route('/api/emotions/diary/<date_str>', methods=['GET'])
    @login_required
    def get_diary_entry(date_str):
        user = get_current_user()
        entry = repository.get_emotion_entry_by_date(user['id'], date_str)
        
        if entry:
            emotion = static_data.get_emotion_by_id(entry['emotion_id'])
            entry_dict = dict(entry)
            entry_dict['emotion'] = emotion
            return jsonify(entry_dict)
        return jsonify(None)
    
    
    @app.route('/api/upload/photo', methods=['POST'])
    @login_required
    def upload_photo():
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
        return jsonify({'photo_url': photo_url, 'filename': unique_filename})
    
    
    @app.route('/api/uploads/<filename>')
    def serve_upload(filename):
        return send_from_directory(UPLOAD_FOLDER, filename)
    
    
    @app.route('/api/emotions/history', methods=['GET'])
    @login_required
    def get_emotion_history():
        user = get_current_user()
        days = request.args.get('days', 30, type=int)
        history = repository.get_emotion_history_by_user(user['id'], days)
        
        result = []
        for entry in history:
            emotion = static_data.get_emotion_by_id(entry['emotion_id'])
            entry_dict = dict(entry)
            entry_dict['emotion'] = emotion
            result.append(entry_dict)
        return jsonify(result)
    
    
    @app.route('/api/emotions/statistics', methods=['GET'])
    @login_required
    def get_emotion_statistics():
        user = get_current_user()
        days = request.args.get('days', 30, type=int)
        stats = recommendation_engine.get_emotion_statistics_from_repo(user['id'], days)
        return jsonify(stats)
    
    
    @app.route('/api/tasks', methods=['GET'])
    @login_required
    def get_tasks():
        user = get_current_user()
        date_str = request.args.get('date')
        tasks = repository.get_tasks_by_user(user['id'], date_str)
        return jsonify(tasks)
    
    
    @app.route('/api/tasks', methods=['POST'])
    @login_required
    def create_task():
        user = get_current_user()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        if not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400
        
        if data.get('task_date'):
            task_date = data['task_date']
        else:
            task_date = datetime.now().strftime('%Y-%m-%d')
        
        existing = repository.get_existing_task(user['id'], data['title'], task_date)
        if existing:
            return jsonify({'error': 'Task already exists', 'task': existing}), 409
        
        category = data.get('category', 'Personal')
        priority = data.get('priority', 'Medium')
        
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
        user = get_current_user()
        task = repository.get_task_by_id(task_id, user['id'])
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        data = request.get_json()
        
        if 'is_completed' in data:
            task = repository.update_task(task_id, user['id'], data['is_completed'])
        
        return jsonify(task)
    
    
    @app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
    @login_required
    def delete_task(task_id):
        user = get_current_user()
        success = repository.delete_task(task_id, user['id'])
        
        if not success:
            return jsonify({'error': 'Task not found'}), 404
        
        return jsonify({'message': 'Task deleted'})
    
    
    @app.route('/api/tasks/recommended', methods=['GET'])
    @login_required
    def get_recommended_tasks():
        user = get_current_user()
        emotion = request.args.get('emotion')
        if not emotion:
            emotion = 'Neutral'
        
        limit = request.args.get('limit', 5, type=int)
        date_str = request.args.get('date')
        
        recommendations = recommendation_engine.get_recommended_tasks_from_repo(user['id'], emotion, limit, date_str)
        return jsonify(recommendations)
    
    
    @app.route('/api/tasks/suggestions', methods=['GET'])
    @login_required
    def get_task_suggestions():
        emotion = request.args.get('emotion')
        if not emotion:
            emotion = 'Neutral'
        
        limit = request.args.get('limit', 3, type=int)
        suggestions = recommendation_engine.get_suggested_tasks(emotion, limit)
        return jsonify(suggestions)
    
    
    @app.route('/api/music/recommendations', methods=['GET'])
    def get_music_recommendations():
        emotion = request.args.get('emotion')
        if not emotion:
            emotion = 'Neutral'
        
        limit = request.args.get('limit', 4, type=int)
        recommendations = static_data.get_music_by_emotion(emotion, limit)
        return jsonify(recommendations)
    
    
    @app.route('/api/books/tags', methods=['GET'])
    def get_book_tags():
        tags = static_data.get_all_book_tags()
        result = []
        
        for tag in tags:
            tag_copy = dict(tag)
            count = 0
            for book in static_data.BOOK_RECOMMENDATIONS:
                if tag['slug'] in book['tags']:
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
        tag_slugs = request.args.getlist('tags')
        if not tag_slugs:
            tag_slugs = request.args.getlist('tags[]')
        
        limit = request.args.get('limit', 24, type=int)
        books = static_data.get_books_by_tags(tag_slugs, limit)
        
        result = []
        for book in books:
            book_copy = dict(book)
            book_copy['tags'] = static_data.get_tag_objects_for_book(book)
            result.append(book_copy)
        
        return jsonify(result)
    
    
    @app.route('/api/user/profile', methods=['GET'])
    @login_required
    def get_profile():
        user = get_current_user()
        return jsonify(repository.user_to_dict(user))
    
    
    @app.route('/api/user/profile', methods=['PUT'])
    @login_required
    def update_profile():
        user = get_current_user()
        data = request.get_json()
        
        if 'username' in data:
            existing = repository.get_user_by_username(data['username'])
            if existing and existing['id'] != user['id']:
                return jsonify({'error': 'Username already taken'}), 400
            user = repository.update_user(user['id'], data['username'])
        
        return jsonify(repository.user_to_dict(user))
    
    
    @app.route('/api/dashboard/summary', methods=['GET'])
    @login_required
    def get_dashboard_summary():
        user = get_current_user()
        today = datetime.now().strftime('%Y-%m-%d')
        
        today_emotion = repository.get_emotion_entry_by_date(user['id'], today)
        
        task_counts = repository.count_tasks(user['id'])
        total_tasks = task_counts['total']
        completed_tasks = task_counts['completed']
        pending_tasks = total_tasks - completed_tasks
        
        today_tasks = repository.get_today_due_tasks(user['id'], today)
        
        emotion_stats = recommendation_engine.get_emotion_statistics_from_repo(user['id'], 7)
        
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
