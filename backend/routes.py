from flask import request, jsonify, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from werkzeug.utils import secure_filename
import recommendation_engine
import os
import uuid

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    if filename and '.' in filename:
        return filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    return False


def register_routes(app, db):
    from models import User, Task, Emotion, EmotionHistory, MusicRecommendation, BookRecommendation, BookTag, BookTagLink
    
    # AUTH API
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        data = request.get_json()
        if not data or not data.get('email') or not data.get('password') or not data.get('username'):
            return jsonify({'error': 'Email, password and username required'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        if User.query.filter_by(username=data['username']).first():
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
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        if not user or not user.check_password(data['password']):
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
        emotions = Emotion.query.all()
        return jsonify([e.to_dict() for e in emotions])
    
    @app.route('/api/emotions/record', methods=['POST'])
    @login_required
    def record_emotion():
        data = request.get_json()
        if not data or not data.get('emotion_id'):
            return jsonify({'error': 'Emotion ID required'}), 400
        
        date = datetime.strptime(data['date'], '%Y-%m-%d').date() if data.get('date') else datetime.now().date()
        existing = EmotionHistory.query.filter_by(user_id=current_user.id, date=date).first()
        
        if existing:
            existing.emotion_id = data['emotion_id']
            existing.notes = data.get('notes', existing.notes)
            existing.photo_url = data.get('photo_url', existing.photo_url)
            existing.recorded_at = datetime.utcnow()
            entry = existing
        else:
            entry = EmotionHistory(user_id=current_user.id, emotion_id=data['emotion_id'], date=date, notes=data.get('notes'), photo_url=data.get('photo_url'))
            db.session.add(entry)
        
        db.session.commit()
        return jsonify({'message': 'Emotion recorded', 'entry': entry.to_dict()})
    
    @app.route('/api/emotions/diary/<date_str>', methods=['GET'])
    @login_required
    def get_diary_entry(date_str):
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
        
        entry = EmotionHistory.query.filter_by(user_id=current_user.id, date=date).first()
        return jsonify(entry.to_dict() if entry else None)
    
    # UPLOAD API
    @app.route('/api/upload/photo', methods=['POST'])
    @login_required
    def upload_photo():
        if 'photo' not in request.files:
            return jsonify({'error': 'No photo provided'}), 400
        
        file = request.files['photo']
        if not file.filename or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file'}), 400
        
        filename = secure_filename(file.filename)
        unique_filename = uuid.uuid4().hex + '_' + filename
        
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        
        file.save(os.path.join(UPLOAD_FOLDER, unique_filename))
        return jsonify({'photo_url': '/api/uploads/' + unique_filename, 'filename': unique_filename})
    
    @app.route('/api/uploads/<filename>')
    def serve_upload(filename):
        return send_from_directory(UPLOAD_FOLDER, filename)
    
    @app.route('/api/emotions/history', methods=['GET'])
    @login_required
    def get_emotion_history():
        days = request.args.get('days', 30, type=int)
        history = EmotionHistory.query.filter_by(user_id=current_user.id).order_by(EmotionHistory.date.desc()).limit(days).all()
        return jsonify([h.to_dict() for h in history])
    
    @app.route('/api/emotions/statistics', methods=['GET'])
    @login_required
    def get_emotion_statistics():
        days = request.args.get('days', 30, type=int)
        return jsonify(recommendation_engine.get_emotion_statistics(db, current_user.id, days))
    
    # TASKS API
    @app.route('/api/tasks', methods=['GET'])
    @login_required
    def get_tasks():
        query = Task.query.filter_by(user_id=current_user.id)
        date_str = request.args.get('date')
        if date_str:
            query = query.filter_by(task_date=datetime.strptime(date_str, '%Y-%m-%d').date())
        tasks = query.order_by(Task.created_at.desc()).all()
        return jsonify([t.to_dict() for t in tasks])
    
    @app.route('/api/tasks', methods=['POST'])
    @login_required
    def create_task():
        data = request.get_json()
        if not data or not data.get('title'):
            return jsonify({'error': 'Title required'}), 400
        
        task_date = datetime.strptime(data['task_date'], '%Y-%m-%d').date() if data.get('task_date') else datetime.now().date()
        
        existing = Task.query.filter_by(user_id=current_user.id, title=data['title'], task_date=task_date, is_completed=False).first()
        if existing:
            return jsonify({'error': 'Task already exists', 'task': existing.to_dict()}), 409
        
        task = Task(user_id=current_user.id, title=data['title'], category=data.get('category', 'Personal'), priority=data.get('priority', 'Medium'), task_date=task_date, recommended_for_emotion=data.get('recommended_for_emotion'))
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
            task.completed_at = datetime.utcnow() if data['is_completed'] else None
        
        db.session.commit()
        return jsonify(task.to_dict())
    
    @app.route('/api/tasks/recommended', methods=['GET'])
    @login_required
    def get_recommended_tasks():
        emotion = request.args.get('emotion', 'Neutral')
        limit = request.args.get('limit', 5, type=int)
        date_str = request.args.get('date')
        task_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else None
        return jsonify(recommendation_engine.get_recommended_tasks(db, current_user.id, emotion, limit, task_date))
    
    @app.route('/api/tasks/suggestions', methods=['GET'])
    @login_required
    def get_task_suggestions():
        emotion = request.args.get('emotion', 'Neutral')
        limit = request.args.get('limit', 3, type=int)
        return jsonify(recommendation_engine.get_suggested_tasks(emotion, limit))
    
    # MUSIC API
    @app.route('/api/music/recommendations', methods=['GET'])
    def get_music_recommendations():
        emotion = request.args.get('emotion', 'Neutral')
        limit = request.args.get('limit', 4, type=int)
        user_id = current_user.id if current_user.is_authenticated else None
        return jsonify(recommendation_engine.get_music_recommendations(db, emotion, user_id, limit))
    
    # BOOKS API
    @app.route('/api/books/tags', methods=['GET'])
    def get_book_tags():
        tags = BookTag.query.all()
        result = []
        for tag in tags:
            tag_dict = tag.to_dict()
            tag_dict['book_count'] = BookTagLink.query.filter_by(tag_id=tag.id).count()
            result.append(tag_dict)
        result.sort(key=lambda x: x['name'])
        return jsonify(result)
    
    @app.route('/api/books', methods=['GET'])
    def get_books_by_tags():
        tag_slugs = request.args.getlist('tags') or request.args.getlist('tags[]')
        limit = request.args.get('limit', 24, type=int)
        
        if not tag_slugs:
            books = BookRecommendation.query.order_by(BookRecommendation.popularity_score.desc()).limit(limit).all()
            return jsonify([b.to_dict() for b in books])
        
        tag_ids = []
        for slug in tag_slugs:
            tag = BookTag.query.filter_by(slug=slug).first()
            if tag:
                tag_ids.append(tag.id)
        
        if not tag_ids:
            return jsonify([])
        
        from sqlalchemy import func
        book_ids = [r[0] for r in db.session.query(BookTagLink.book_id).filter(BookTagLink.tag_id.in_(tag_ids)).group_by(BookTagLink.book_id).having(func.count(BookTagLink.tag_id) == len(tag_ids)).all()]
        
        if not book_ids:
            return jsonify([])
        
        books = BookRecommendation.query.filter(BookRecommendation.id.in_(book_ids)).order_by(BookRecommendation.popularity_score.desc()).limit(limit).all()
        return jsonify([b.to_dict() for b in books])
    
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
        
        total = Task.query.filter_by(user_id=current_user.id).count()
        completed = Task.query.filter_by(user_id=current_user.id, is_completed=True).count()
        
        today_tasks = Task.query.filter_by(user_id=current_user.id, due_date=today, is_completed=False).all()
        
        return jsonify({
            'user': current_user.to_dict(),
            'today_emotion': today_emotion.to_dict() if today_emotion else None,
            'task_summary': {'total': total, 'completed': completed, 'pending': total - completed},
            'today_tasks': [t.to_dict() for t in today_tasks],
            'weekly_mood_stats': recommendation_engine.get_emotion_statistics(db, current_user.id, 7)
        })
