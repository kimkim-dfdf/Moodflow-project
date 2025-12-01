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
    from models import User, Task, Emotion, EmotionHistory, CalendarEvent, MusicRecommendation
    
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
    
    @app.route('/api/emotions/analyze', methods=['POST'])
    @login_required
    def analyze_mood():
        data = request.get_json()
        
        sleep_quality = data.get('sleep_quality', 3)
        energy_level = data.get('energy_level', 3)
        stress_level = data.get('stress_level', 3)
        concentration = data.get('concentration', 3)
        motivation = data.get('motivation', 3)
        mood_rating = data.get('mood_rating', 3)
        
        emotion_id = EmotionRecommendationEngine.analyze_mood_factors(
            db, sleep_quality, energy_level, stress_level, concentration, motivation, mood_rating
        )
        
        return jsonify({'emotion_id': emotion_id})
    
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
            existing.sleep_quality = data.get('sleep_quality', existing.sleep_quality)
            existing.energy_level = data.get('energy_level', existing.energy_level)
            existing.stress_level = data.get('stress_level', existing.stress_level)
            existing.concentration = data.get('concentration', existing.concentration)
            existing.motivation = data.get('motivation', existing.motivation)
            existing.mood_rating = data.get('mood_rating', existing.mood_rating)
            existing.recorded_at = datetime.utcnow()
            entry = existing
        else:
            entry = EmotionHistory(
                user_id=current_user.id,
                emotion_id=data['emotion_id'],
                date=date,
                notes=data.get('notes'),
                photo_url=data.get('photo_url'),
                sleep_quality=data.get('sleep_quality'),
                energy_level=data.get('energy_level'),
                stress_level=data.get('stress_level'),
                concentration=data.get('concentration'),
                motivation=data.get('motivation'),
                mood_rating=data.get('mood_rating')
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
    
    @app.route('/api/emotions/today', methods=['GET'])
    @login_required
    def get_today_emotion():
        today = datetime.now().date()
        entry = EmotionHistory.query.filter_by(
            user_id=current_user.id,
            date=today
        ).first()
        
        if entry:
            return jsonify(entry.to_dict())
        return jsonify(None)
    
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
        status = request.args.get('status')
        category = request.args.get('category')
        
        query = Task.query.filter_by(user_id=current_user.id)
        
        if status == 'completed':
            query = query.filter_by(is_completed=True)
        elif status == 'incomplete':
            query = query.filter_by(is_completed=False)
        
        if category:
            query = query.filter_by(category=category)
        
        tasks = query.order_by(Task.created_at.desc()).all()
        return jsonify([t.to_dict() for t in tasks])
    
    @app.route('/api/tasks', methods=['POST'])
    @login_required
    def create_task():
        data = request.get_json()
        
        if not data or not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400
        
        task = Task(
            user_id=current_user.id,
            title=data['title'],
            description=data.get('description'),
            category=data.get('category', 'Personal'),
            priority=data.get('priority', 'Medium'),
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date() if data.get('due_date') else None,
            recommended_for_emotion=data.get('recommended_for_emotion')
        )
        
        db.session.add(task)
        db.session.commit()
        
        return jsonify(task.to_dict()), 201
    
    @app.route('/api/tasks/<int:task_id>', methods=['GET'])
    @login_required
    def get_task(task_id):
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        return jsonify(task.to_dict())
    
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
        return jsonify({'message': 'Task deleted successfully'})
    
    @app.route('/api/tasks/recommended', methods=['GET'])
    @login_required
    def get_recommended_tasks():
        emotion_name = request.args.get('emotion', 'Neutral')
        limit = request.args.get('limit', 5, type=int)
        
        recommendations = EmotionRecommendationEngine.get_recommended_tasks(
            db, current_user.id, emotion_name, limit
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
    
    @app.route('/api/calendar/events', methods=['GET'])
    @login_required
    def get_calendar_events():
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        
        query = CalendarEvent.query.filter_by(user_id=current_user.id)
        
        if month and year:
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)
            query = query.filter(
                CalendarEvent.start_date >= start_date,
                CalendarEvent.start_date < end_date
            )
        
        events = query.order_by(CalendarEvent.start_date).all()
        return jsonify([e.to_dict() for e in events])
    
    @app.route('/api/calendar/events', methods=['POST'])
    @login_required
    def create_calendar_event():
        data = request.get_json()
        
        if not data or not data.get('title') or not data.get('start_date'):
            return jsonify({'error': 'Title and start date are required'}), 400
        
        event = CalendarEvent(
            user_id=current_user.id,
            title=data['title'],
            description=data.get('description'),
            start_date=datetime.fromisoformat(data['start_date'].replace('Z', '+00:00')),
            end_date=datetime.fromisoformat(data['end_date'].replace('Z', '+00:00')) if data.get('end_date') else None,
            all_day=data.get('all_day', False),
            color=data.get('color', '#6366f1')
        )
        
        db.session.add(event)
        db.session.commit()
        
        return jsonify(event.to_dict()), 201
    
    @app.route('/api/calendar/events/<int:event_id>', methods=['PUT'])
    @login_required
    def update_calendar_event(event_id):
        event = CalendarEvent.query.filter_by(id=event_id, user_id=current_user.id).first()
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        data = request.get_json()
        
        if 'title' in data:
            event.title = data['title']
        if 'description' in data:
            event.description = data['description']
        if 'start_date' in data:
            event.start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
        if 'end_date' in data:
            event.end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00')) if data['end_date'] else None
        if 'all_day' in data:
            event.all_day = data['all_day']
        if 'color' in data:
            event.color = data['color']
        
        db.session.commit()
        return jsonify(event.to_dict())
    
    @app.route('/api/calendar/events/<int:event_id>', methods=['DELETE'])
    @login_required
    def delete_calendar_event(event_id):
        event = CalendarEvent.query.filter_by(id=event_id, user_id=current_user.id).first()
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        db.session.delete(event)
        db.session.commit()
        return jsonify({'message': 'Event deleted successfully'})
    
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
