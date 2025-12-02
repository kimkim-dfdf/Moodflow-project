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
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    if ext in ALLOWED_EXTENSIONS:
        return True
    return False


def register_routes(app, db):
    from models import User, Task, Emotion, EmotionHistory, MusicRecommendation, BookRecommendation, BookTag, BookTagLink
    
    # ============================================
    # AUTH API
    # ============================================
    
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        data = request.get_json()
        
        # Check required fields
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        if not data.get('email'):
            return jsonify({'error': 'Email is required'}), 400
        if not data.get('password'):
            return jsonify({'error': 'Password is required'}), 400
        if not data.get('username'):
            return jsonify({'error': 'Username is required'}), 400
        
        # Check if email exists
        existing_email = User.query.filter_by(email=data['email']).first()
        if existing_email:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Check if username exists
        existing_username = User.query.filter_by(username=data['username']).first()
        if existing_username:
            return jsonify({'error': 'Username already taken'}), 400
        
        # Create user
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
        
        # Check required fields
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        if not data.get('email'):
            return jsonify({'error': 'Email is required'}), 400
        if not data.get('password'):
            return jsonify({'error': 'Password is required'}), 400
        
        # Find user
        user = User.query.filter_by(email=data['email']).first()
        
        # Check password
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
    
    # ============================================
    # EMOTIONS API
    # ============================================
    
    @app.route('/api/emotions', methods=['GET'])
    def get_emotions():
        emotions = Emotion.query.all()
        result = []
        for emotion in emotions:
            result.append(emotion.to_dict())
        return jsonify(result)
    
    @app.route('/api/emotions/record', methods=['POST'])
    @login_required
    def record_emotion():
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        if not data.get('emotion_id'):
            return jsonify({'error': 'Emotion ID is required'}), 400
        
        # Get date
        date = datetime.now().date()
        if data.get('date'):
            date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        
        # Check if entry exists
        existing = EmotionHistory.query.filter_by(
            user_id=current_user.id,
            date=date
        ).first()
        
        if existing:
            # Update existing
            existing.emotion_id = data['emotion_id']
            if data.get('notes'):
                existing.notes = data['notes']
            if data.get('photo_url'):
                existing.photo_url = data['photo_url']
            existing.recorded_at = datetime.utcnow()
            entry = existing
        else:
            # Create new
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
        # Parse date
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
        
        # Find entry
        entry = EmotionHistory.query.filter_by(
            user_id=current_user.id,
            date=date
        ).first()
        
        if entry:
            return jsonify(entry.to_dict())
        return jsonify(None)
    
    # ============================================
    # UPLOAD API
    # ============================================
    
    @app.route('/api/upload/photo', methods=['POST'])
    @login_required
    def upload_photo():
        # Check if file exists
        if 'photo' not in request.files:
            return jsonify({'error': 'No photo provided'}), 400
        
        file = request.files['photo']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file type
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Create filename
        filename = secure_filename(file.filename)
        unique_filename = uuid.uuid4().hex + '_' + filename
        
        # Create folder if needed
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        
        # Save file
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
        
        history = EmotionHistory.query.filter_by(
            user_id=current_user.id
        ).order_by(EmotionHistory.date.desc()).limit(days).all()
        
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
    
    # ============================================
    # TASKS API
    # ============================================
    
    @app.route('/api/tasks', methods=['GET'])
    @login_required
    def get_tasks():
        date_str = request.args.get('date')
        
        query = Task.query.filter_by(user_id=current_user.id)
        
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
        
        # Get task date
        task_date = datetime.now().date()
        if data.get('task_date'):
            task_date = datetime.strptime(data['task_date'], '%Y-%m-%d').date()
        
        # Check for duplicate
        existing_task = Task.query.filter_by(
            user_id=current_user.id,
            title=data['title'],
            task_date=task_date,
            is_completed=False
        ).first()
        
        if existing_task:
            return jsonify({'error': 'This task already exists for this date', 'task': existing_task.to_dict()}), 409
        
        # Get category
        category = 'Personal'
        if data.get('category'):
            category = data['category']
        
        # Get priority
        priority = 'Medium'
        if data.get('priority'):
            priority = data['priority']
        
        # Create task
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
        
        # Update completion status
        if 'is_completed' in data:
            task.is_completed = data['is_completed']
            if data['is_completed']:
                task.completed_at = datetime.utcnow()
            else:
                task.completed_at = None
        
        db.session.commit()
        return jsonify(task.to_dict())
    
    @app.route('/api/tasks/recommended', methods=['GET'])
    @login_required
    def get_recommended_tasks():
        emotion_name = request.args.get('emotion')
        if not emotion_name:
            emotion_name = 'Neutral'
        
        limit = request.args.get('limit', 5, type=int)
        date_str = request.args.get('date')
        
        task_date = None
        if date_str:
            task_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        recommendations = recommendation_engine.get_recommended_tasks(
            db, current_user.id, emotion_name, limit, task_date
        )
        return jsonify(recommendations)
    
    @app.route('/api/tasks/suggestions', methods=['GET'])
    @login_required
    def get_task_suggestions():
        emotion_name = request.args.get('emotion')
        if not emotion_name:
            emotion_name = 'Neutral'
        
        limit = request.args.get('limit', 3, type=int)
        
        suggestions = recommendation_engine.get_suggested_tasks(emotion_name, limit)
        return jsonify(suggestions)
    
    # ============================================
    # MUSIC API
    # ============================================
    
    @app.route('/api/music/recommendations', methods=['GET'])
    def get_music_recommendations():
        emotion_name = request.args.get('emotion')
        if not emotion_name:
            emotion_name = 'Neutral'
        
        limit = request.args.get('limit', 4, type=int)
        
        user_id = None
        if current_user.is_authenticated:
            user_id = current_user.id
        
        recommendations = recommendation_engine.get_music_recommendations(
            db, emotion_name, user_id, limit
        )
        return jsonify(recommendations)
    
    # ============================================
    # BOOKS API
    # ============================================
    
    @app.route('/api/books/tags', methods=['GET'])
    def get_book_tags():
        # Get all tags with book count
        tags = BookTag.query.all()
        
        result = []
        for tag in tags:
            # Count books with this tag
            book_count = BookTagLink.query.filter_by(tag_id=tag.id).count()
            
            tag_dict = tag.to_dict()
            tag_dict['book_count'] = book_count
            result.append(tag_dict)
        
        # Sort by name
        result.sort(key=lambda x: x['name'])
        
        return jsonify(result)
    
    @app.route('/api/books', methods=['GET'])
    def get_books_by_tags():
        # Get tag parameters
        tag_slugs = request.args.getlist('tags')
        if not tag_slugs:
            tag_slugs = request.args.getlist('tags[]')
        
        limit = request.args.get('limit', 24, type=int)
        
        # If no tags selected, return all books
        if not tag_slugs:
            books = BookRecommendation.query.order_by(
                BookRecommendation.popularity_score.desc()
            ).limit(limit).all()
            
            result = []
            for book in books:
                result.append(book.to_dict())
            return jsonify(result)
        
        # Find tag IDs
        tag_ids = []
        for slug in tag_slugs:
            tag = BookTag.query.filter_by(slug=slug).first()
            if tag:
                tag_ids.append(tag.id)
        
        if not tag_ids:
            return jsonify([])
        
        # Find books that have ALL selected tags (AND logic)
        from sqlalchemy import func
        
        book_ids_query = db.session.query(BookTagLink.book_id).filter(
            BookTagLink.tag_id.in_(tag_ids)
        ).group_by(BookTagLink.book_id).having(
            func.count(BookTagLink.tag_id) == len(tag_ids)
        ).all()
        
        book_ids = []
        for row in book_ids_query:
            book_ids.append(row[0])
        
        if not book_ids:
            return jsonify([])
        
        # Get books
        books = BookRecommendation.query.filter(
            BookRecommendation.id.in_(book_ids)
        ).order_by(
            BookRecommendation.popularity_score.desc()
        ).limit(limit).all()
        
        result = []
        for book in books:
            result.append(book.to_dict())
        
        return jsonify(result)
    
    # ============================================
    # PROFILE API
    # ============================================
    
    @app.route('/api/user/profile', methods=['GET'])
    @login_required
    def get_profile():
        return jsonify(current_user.to_dict())
    
    @app.route('/api/user/profile', methods=['PUT'])
    @login_required
    def update_profile():
        data = request.get_json()
        
        if 'username' in data:
            # Check if username is taken
            existing = User.query.filter_by(username=data['username']).first()
            if existing:
                if existing.id != current_user.id:
                    return jsonify({'error': 'Username already taken'}), 400
            current_user.username = data['username']
        
        db.session.commit()
        return jsonify(current_user.to_dict())
    
    # ============================================
    # DASHBOARD API
    # ============================================
    
    @app.route('/api/dashboard/summary', methods=['GET'])
    @login_required
    def get_dashboard_summary():
        today = datetime.now().date()
        
        # Get today's emotion
        today_emotion = EmotionHistory.query.filter_by(
            user_id=current_user.id,
            date=today
        ).first()
        
        # Count tasks
        total_tasks = Task.query.filter_by(user_id=current_user.id).count()
        completed_tasks = Task.query.filter_by(user_id=current_user.id, is_completed=True).count()
        pending_tasks = total_tasks - completed_tasks
        
        # Get today's tasks
        today_tasks = Task.query.filter_by(
            user_id=current_user.id,
            due_date=today,
            is_completed=False
        ).all()
        
        today_tasks_list = []
        for task in today_tasks:
            today_tasks_list.append(task.to_dict())
        
        # Get emotion statistics
        emotion_stats = recommendation_engine.get_emotion_statistics(db, current_user.id, 7)
        
        # Build response
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
