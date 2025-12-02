from flask import request, jsonify, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from recommendation_engine import EmotionRecommendationEngine
from werkzeug.utils import secure_filename
import os
import uuid

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def register_routes(app, db):
    from models import User, Task, Emotion, EmotionHistory, MusicRecommendation, BookRecommendation, BookTag, BookTagLink
    
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password') or not data.get('username'):
            return jsonify({'error': 'Email, username, and password are required'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already taken'}), 400
        
        user = User(
            email=data['email'],
            username=data['username']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return jsonify({'message': 'Registration successful', 'user': user.to_dict()}), 201
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
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
    
    @app.route('/api/emotions', methods=['GET'])
    def get_emotions():
        emotions = Emotion.query.all()
        return jsonify([e.to_dict() for e in emotions])
    
    @app.route('/api/emotions/record', methods=['POST'])
    @login_required
    def record_emotion():
        data = request.get_json()
        
        if not data or not data.get('emotion_id'):
            return jsonify({'error': 'Emotion ID is required'}), 400
        
        date = datetime.now().date()
        if data.get('date'):
            date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        
        existing = EmotionHistory.query.filter_by(
            user_id=current_user.id,
            date=date
        ).first()
        
        if existing:
            existing.emotion_id = data['emotion_id']
            existing.notes = data.get('notes', existing.notes)
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
        return jsonify({'message': 'Emotion recorded successfully', 'entry': entry.to_dict()})
    
    @app.route('/api/emotions/diary/<date_str>', methods=['GET'])
    @login_required
    def get_diary_entry(date_str):
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
        
        entry = EmotionHistory.query.filter_by(
            user_id=current_user.id,
            date=date
        ).first()
        
        if entry:
            return jsonify(entry.to_dict())
        return jsonify(None)
    
    @app.route('/api/upload/photo', methods=['POST'])
    @login_required
    def upload_photo():
        if 'photo' not in request.files:
            return jsonify({'error': 'No photo provided'}), 400
        
        file = request.files['photo']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(file_path)
            
            photo_url = f"/api/uploads/{unique_filename}"
            return jsonify({'photo_url': photo_url, 'filename': unique_filename})
        
        return jsonify({'error': 'Invalid file type'}), 400
    
    @app.route('/api/uploads/<filename>')
    def serve_upload(filename):
        return send_from_directory(UPLOAD_FOLDER, filename)
    
    @app.route('/api/emotions/history', methods=['GET'])
    @login_required
    def get_emotion_history():
        days = request.args.get('days', 30, type=int)
        history = EmotionHistory.query.filter_by(
            user_id=current_user.id
        ).order_by(EmotionHistory.date.desc()).limit(days).all()
        return jsonify([h.to_dict() for h in history])
    
    @app.route('/api/emotions/statistics', methods=['GET'])
    @login_required
    def get_emotion_statistics():
        days = request.args.get('days', 30, type=int)
        stats = EmotionRecommendationEngine.get_emotion_statistics(db, current_user.id, days)
        return jsonify(stats)
    
    @app.route('/api/tasks', methods=['GET'])
    @login_required
    def get_tasks():
        date_str = request.args.get('date')
        
        query = Task.query.filter_by(user_id=current_user.id)
        
        if date_str:
            task_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            query = query.filter_by(task_date=task_date)
        
        tasks = query.order_by(Task.created_at.desc()).all()
        return jsonify([t.to_dict() for t in tasks])
    
    @app.route('/api/tasks', methods=['POST'])
    @login_required
    def create_task():
        data = request.get_json()
        
        if not data or not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400
        
        task_date = datetime.now().date()
        if data.get('task_date'):
            task_date = datetime.strptime(data['task_date'], '%Y-%m-%d').date()
        
        existing_task = Task.query.filter_by(
            user_id=current_user.id,
            title=data['title'],
            task_date=task_date,
            is_completed=False
        ).first()
        
        if existing_task:
            return jsonify({'error': 'This task already exists for this date', 'task': existing_task.to_dict()}), 409
        
        task = Task(
            user_id=current_user.id,
            title=data['title'],
            description=data.get('description'),
            category=data.get('category', 'Personal'),
            priority=data.get('priority', 'Medium'),
            task_date=task_date,
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date() if data.get('due_date') else None,
            due_time=data.get('due_time'),
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
        
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'category' in data:
            task.category = data['category']
        if 'priority' in data:
            task.priority = data['priority']
        if 'is_completed' in data:
            task.is_completed = data['is_completed']
            if data['is_completed']:
                task.completed_at = datetime.utcnow()
            else:
                task.completed_at = None
        if 'due_date' in data:
            task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date() if data['due_date'] else None
        if 'due_time' in data:
            task.due_time = data['due_time'] if data['due_time'] else None
        
        db.session.commit()
        return jsonify(task.to_dict())
    
    @app.route('/api/tasks/recommended', methods=['GET'])
    @login_required
    def get_recommended_tasks():
        emotion_name = request.args.get('emotion', 'Neutral')
        limit = request.args.get('limit', 5, type=int)
        date_str = request.args.get('date')
        
        task_date = None
        if date_str:
            task_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        recommendations = EmotionRecommendationEngine.get_recommended_tasks(
            db, current_user.id, emotion_name, limit, task_date
        )
        return jsonify(recommendations)
    
    @app.route('/api/tasks/suggestions', methods=['GET'])
    @login_required
    def get_task_suggestions():
        emotion_name = request.args.get('emotion', 'Neutral')
        limit = request.args.get('limit', 3, type=int)
        
        suggestions = EmotionRecommendationEngine.get_suggested_tasks(emotion_name, limit)
        return jsonify(suggestions)
    
    @app.route('/api/music/recommendations', methods=['GET'])
    def get_music_recommendations():
        emotion_name = request.args.get('emotion', 'Neutral')
        limit = request.args.get('limit', 4, type=int)
        
        user_id = current_user.id if current_user.is_authenticated else None
        recommendations = EmotionRecommendationEngine.get_music_recommendations(
            db, emotion_name, user_id, limit
        )
        return jsonify(recommendations)
    
    @app.route('/api/books/tags', methods=['GET'])
    def get_book_tags():
        tags = db.session.query(
            BookTag,
            db.func.count(BookTagLink.book_id).label('book_count')
        ).outerjoin(BookTagLink, BookTag.id == BookTagLink.tag_id)\
         .group_by(BookTag.id)\
         .order_by(BookTag.name)\
         .all()
        
        result = []
        for tag, count in tags:
            tag_dict = tag.to_dict()
            tag_dict['book_count'] = count
            result.append(tag_dict)
        
        return jsonify(result)
    
    @app.route('/api/books', methods=['GET'])
    def get_books_by_tags():
        tag_slugs = request.args.getlist('tags') or request.args.getlist('tags[]')
        limit = request.args.get('limit', 24, type=int)
        
        if not tag_slugs:
            books = BookRecommendation.query\
                .order_by(BookRecommendation.popularity_score.desc())\
                .limit(limit)\
                .all()
            return jsonify([b.to_dict() for b in books])
        
        selected_tags = BookTag.query.filter(BookTag.slug.in_(tag_slugs)).all()
        tag_ids = [t.id for t in selected_tags]
        
        if not tag_ids:
            return jsonify([])
        
        book_match_counts = db.session.query(
            BookTagLink.book_id,
            db.func.count(BookTagLink.tag_id).label('match_count')
        ).filter(BookTagLink.tag_id.in_(tag_ids))\
         .group_by(BookTagLink.book_id)\
         .all()
        
        book_scores = {book_id: count for book_id, count in book_match_counts}
        book_ids = list(book_scores.keys())
        
        books = BookRecommendation.query\
            .filter(BookRecommendation.id.in_(book_ids))\
            .all()
        
        total_selected = len(tag_slugs)
        result = []
        for book in books:
            book_dict = book.to_dict()
            match_count = book_scores.get(book.id, 0)
            book_tags_count = len(book_dict.get('tags', []))
            union = total_selected + book_tags_count - match_count
            jaccard_score = match_count / union if union > 0 else 0
            book_dict['match_count'] = match_count
            book_dict['total_selected'] = total_selected
            book_dict['match_score'] = round(jaccard_score * 100)
            result.append(book_dict)
        
        result.sort(key=lambda x: (-x['match_count'], -x.get('popularity_score', 0)))
        
        return jsonify(result[:limit])
    
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
        
        if 'preferred_work_time' in data:
            current_user.preferred_work_time = data['preferred_work_time']
        
        if 'preferred_categories' in data:
            if isinstance(data['preferred_categories'], list):
                current_user.preferred_categories = ','.join(data['preferred_categories'])
            else:
                current_user.preferred_categories = data['preferred_categories']
        
        if 'notification_enabled' in data:
            current_user.notification_enabled = data['notification_enabled']
        
        db.session.commit()
        return jsonify(current_user.to_dict())
    
    @app.route('/api/dashboard/summary', methods=['GET'])
    @login_required
    def get_dashboard_summary():
        today = datetime.now().date()
        
        today_emotion = EmotionHistory.query.filter_by(
            user_id=current_user.id,
            date=today
        ).first()
        
        total_tasks = Task.query.filter_by(user_id=current_user.id).count()
        completed_tasks = Task.query.filter_by(user_id=current_user.id, is_completed=True).count()
        pending_tasks = total_tasks - completed_tasks
        
        today_tasks = Task.query.filter_by(
            user_id=current_user.id,
            due_date=today,
            is_completed=False
        ).all()
        
        emotion_stats = EmotionRecommendationEngine.get_emotion_statistics(db, current_user.id, 7)
        
        return jsonify({
            'user': current_user.to_dict(),
            'today_emotion': today_emotion.to_dict() if today_emotion else None,
            'task_summary': {
                'total': total_tasks,
                'completed': completed_tasks,
                'pending': pending_tasks
            },
            'today_tasks': [t.to_dict() for t in today_tasks],
            'weekly_mood_stats': emotion_stats
        })
