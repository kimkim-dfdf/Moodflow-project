from flask import request, jsonify, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from werkzeug.utils import secure_filename
import recommendation_engine
import static_data
import os
import uuid

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    if filename and '.' in filename:
        ext = filename.rsplit('.', 1)[1].lower()
        if ext in ALLOWED_EXTENSIONS:
            return True
    return False


def register_routes(app, db):
    from models import User, Task, EmotionHistory
    
    # AUTH API
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
        
        existing_email = User.query.filter_by(email=data['email']).first()
        if existing_email:
            return jsonify({'error': 'Email already registered'}), 400
        
        existing_username = User.query.filter_by(username=data['username']).first()
        if existing_username:
            return jsonify({'error': 'Username already taken'}), 400
        
        user = User(email=data['email'], username=data['username'])
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        login_user(user)
        
        return jsonify({'message': 'Registration successful', 'user': user.to_dict()}), 201
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        if not data.get('email'):
            return jsonify({'error': 'Email is required'}), 400
        if not data.get('password'):
            return jsonify({'error': 'Password is required'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        if not user.check_password(data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        login_user(user)
        return jsonify({'message': 'Login successful', 'user': user.to_dict()})
    
    @app.route('/api/auth/logout', methods=['POST'])
    @login_required
    def logout():
        logout_user()
        return jsonify({'message': 'Logged out successfully'})
    
    @app.route('/api/auth/me', methods=['GET'])
    @login_required
    def get_current_user():
        return jsonify({'user': current_user.to_dict()})
    
    # EMOTIONS API
    @app.route('/api/emotions', methods=['GET'])
    def get_emotions():
        return jsonify(static_data.EMOTIONS)
    
    @app.route('/api/emotions/record', methods=['POST'])
    @login_required
    def record_emotion():
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        if not data.get('emotion_id'):
            return jsonify({'error': 'Emotion ID is required'}), 400
        
        if data.get('date'):
            date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        else:
            date = datetime.now().date()
        
        existing = EmotionHistory.query.filter_by(user_id=current_user.id, date=date).first()
        
        if existing:
            existing.emotion_id = data['emotion_id']
            if data.get('notes'):
                existing.notes = data['notes']
            if data.get('photo_url'):
                existing.photo_url = data['photo_url']
            existing.recorded_at = datetime.utcnow()
            entry = existing
        else:
            entry = EmotionHistory(
                user_id=current_user.id,
                emotion_id=data['emotion_id'],
                date=date,
                notes=data.get('notes'),
                photo_url=data.get('photo_url')
            )
            db.session.add(entry)
        
        db.session.commit()
        return jsonify({'message': 'Emotion recorded', 'entry': entry.to_dict()})
    
    @app.route('/api/emotions/diary/<date_str>', methods=['GET'])
    @login_required
    def get_diary_entry(date_str):
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except:
            return jsonify({'error': 'Invalid date format'}), 400
        
        entry = EmotionHistory.query.filter_by(user_id=current_user.id, date=date).first()
        if entry:
            return jsonify(entry.to_dict())
        return jsonify(None)
    
    # UPLOAD API
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
        days = request.args.get('days', 30, type=int)
        history = EmotionHistory.query.filter_by(user_id=current_user.id).order_by(EmotionHistory.date.desc()).limit(days).all()
        
        result = []
        for entry in history:
            result.append(entry.to_dict())
        return jsonify(result)
    
    @app.route('/api/emotions/statistics', methods=['GET'])
    @login_required
    def get_emotion_statistics():
        days = request.args.get('days', 30, type=int)
        stats = recommendation_engine.get_emotion_statistics(db, current_user.id, days)
        return jsonify(stats)
    
    # TASKS API
    @app.route('/api/tasks', methods=['GET'])
    @login_required
    def get_tasks():
        query = Task.query.filter_by(user_id=current_user.id)
        
        date_str = request.args.get('date')
        if date_str:
            task_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            query = query.filter_by(task_date=task_date)
        
        tasks = query.order_by(Task.created_at.desc()).all()
        
        result = []
        for task in tasks:
            result.append(task.to_dict())
        return jsonify(result)
    
    @app.route('/api/tasks', methods=['POST'])
    @login_required
    def create_task():
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        if not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400
        
        if data.get('task_date'):
            task_date = datetime.strptime(data['task_date'], '%Y-%m-%d').date()
        else:
            task_date = datetime.now().date()
        
        existing = Task.query.filter_by(
            user_id=current_user.id,
            title=data['title'],
            task_date=task_date,
            is_completed=False
        ).first()
        
        if existing:
            return jsonify({'error': 'Task already exists', 'task': existing.to_dict()}), 409
        
        category = data.get('category', 'Personal')
        priority = data.get('priority', 'Medium')
        
        task = Task(
            user_id=current_user.id,
            title=data['title'],
            category=category,
            priority=priority,
            task_date=task_date,
            recommended_for_emotion=data.get('recommended_for_emotion')
        )
        db.session.add(task)
        db.session.commit()
        
        return jsonify(task.to_dict()), 201
    
    @app.route('/api/tasks/<int:task_id>', methods=['PUT'])
    @login_required
    def update_task(task_id):
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        data = request.get_json()
        
        if 'is_completed' in data:
            task.is_completed = data['is_completed']
            if data['is_completed']:
                task.completed_at = datetime.utcnow()
            else:
                task.completed_at = None
        
        db.session.commit()
        return jsonify(task.to_dict())
    
    @app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
    @login_required
    def delete_task(task_id):
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deleted'})
    
    @app.route('/api/tasks/recommended', methods=['GET'])
    @login_required
    def get_recommended_tasks():
        emotion = request.args.get('emotion')
        if not emotion:
            emotion = 'Neutral'
        
        limit = request.args.get('limit', 5, type=int)
        date_str = request.args.get('date')
        
        task_date = None
        if date_str:
            task_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        recommendations = recommendation_engine.get_recommended_tasks(db, current_user.id, emotion, limit, task_date)
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
    
    # MUSIC API
    @app.route('/api/music/recommendations', methods=['GET'])
    def get_music_recommendations():
        emotion = request.args.get('emotion')
        if not emotion:
            emotion = 'Neutral'
        
        limit = request.args.get('limit', 4, type=int)
        recommendations = static_data.get_music_by_emotion(emotion, limit)
        return jsonify(recommendations)
    
    # BOOKS API
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
    
    # PROFILE API
    @app.route('/api/user/profile', methods=['GET'])
    @login_required
    def get_profile():
        return jsonify(current_user.to_dict())
    
    @app.route('/api/user/profile', methods=['PUT'])
    @login_required
    def update_profile():
        data = request.get_json()
        
        if 'username' in data:
            existing = User.query.filter_by(username=data['username']).first()
            if existing and existing.id != current_user.id:
                return jsonify({'error': 'Username already taken'}), 400
            current_user.username = data['username']
        
        db.session.commit()
        return jsonify(current_user.to_dict())
    
    # DASHBOARD API
    @app.route('/api/dashboard/summary', methods=['GET'])
    @login_required
    def get_dashboard_summary():
        today = datetime.now().date()
        
        today_emotion = EmotionHistory.query.filter_by(user_id=current_user.id, date=today).first()
        
        total_tasks = Task.query.filter_by(user_id=current_user.id).count()
        completed_tasks = Task.query.filter_by(user_id=current_user.id, is_completed=True).count()
        pending_tasks = total_tasks - completed_tasks
        
        today_tasks = Task.query.filter_by(user_id=current_user.id, due_date=today, is_completed=False).all()
        
        today_tasks_list = []
        for task in today_tasks:
            today_tasks_list.append(task.to_dict())
        
        emotion_stats = recommendation_engine.get_emotion_statistics(db, current_user.id, 7)
        
        today_emotion_dict = None
        if today_emotion:
            today_emotion_dict = today_emotion.to_dict()
        
        return jsonify({
            'user': current_user.to_dict(),
            'today_emotion': today_emotion_dict,
            'task_summary': {
                'total': total_tasks,
                'completed': completed_tasks,
                'pending': pending_tasks
            },
            'today_tasks': today_tasks_list,
            'weekly_mood_stats': emotion_stats
        })
