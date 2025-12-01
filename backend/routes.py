# -*- coding: utf-8 -*-
"""
MoodFlow API 라우트 정의
- 인증, 감정 기록, 할일 관리, 캘린더, 음악 추천 등 모든 API 엔드포인트
- 작성일: 2024년
"""

from flask import request, jsonify, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from recommendation_engine import EmotionRecommendationEngine
from werkzeug.utils import secure_filename
import os
import uuid

# 사진 업로드 설정
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    """업로드 가능한 파일 형식인지 확인"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def register_routes(app, db):
    """
    Flask 앱에 모든 API 라우트 등록
    
    API 구조:
    - /api/auth/*     : 인증 관련 (로그인, 회원가입, 로그아웃)
    - /api/emotions/* : 감정 기록 및 조회
    - /api/tasks/*    : 할일 CRUD 및 추천
    - /api/calendar/* : 캘린더 일정 관리
    - /api/music/*    : 음악 추천
    - /api/user/*     : 사용자 프로필
    """
    from models import User, Task, Emotion, EmotionHistory, CalendarEvent, MusicRecommendation
    
    # ============================================
    # 인증 API
    # ============================================
    
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        """회원가입 처리"""
        data = request.get_json()
        
        # 필수 정보 체크
        if not data or not data.get('email') or not data.get('password') or not data.get('username'):
            return jsonify({'error': 'Email, username, and password are required'}), 400
        
        # 이메일 중복 체크
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # 사용자명 중복 체크
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already taken'}), 400
        
        # 새 사용자 생성
        new_user = User(
            email=data['email'],
            username=data['username']
        )
        new_user.set_password(data['password'])
        
        db.session.add(new_user)
        db.session.commit()
        
        # 바로 로그인 처리
        login_user(new_user)
        return jsonify({
            'message': 'Registration successful', 
            'user': new_user.to_dict()
        }), 201
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """로그인 처리"""
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        # 사용자 찾기
        user = User.query.filter_by(email=data['email']).first()
        
        # 비밀번호 확인
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        login_user(user)
        return jsonify({
            'message': 'Login successful', 
            'user': user.to_dict()
        })
    
    @app.route('/api/auth/logout', methods=['POST'])
    @login_required
    def logout():
        """로그아웃 처리"""
        logout_user()
        return jsonify({'message': 'Logged out successfully'})
    
    @app.route('/api/auth/me', methods=['GET'])
    @login_required
    def get_current_user():
        """현재 로그인한 사용자 정보 조회"""
        return jsonify({'user': current_user.to_dict()})
    
    # ============================================
    # 감정 API
    # ============================================
    
    @app.route('/api/emotions', methods=['GET'])
    def get_emotions():
        """사용 가능한 감정 목록 조회 (Happy, Sad, Angry 등)"""
        emotions = Emotion.query.all()
        return jsonify([e.to_dict() for e in emotions])
    
    @app.route('/api/emotions/record', methods=['POST'])
    @login_required
    def record_emotion():
        """오늘의 감정 기록하기"""
        data = request.get_json()
        
        if not data or not data.get('emotion_id'):
            return jsonify({'error': 'Emotion ID is required'}), 400
        
        # 날짜 파싱 (없으면 오늘 날짜)
        record_date = datetime.now().date()
        if data.get('date'):
            record_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        
        # 이미 해당 날짜에 기록이 있는지 확인
        existing = EmotionHistory.query.filter_by(
            user_id=current_user.id,
            date=record_date
        ).first()
        
        if existing:
            # 기존 기록 업데이트
            existing.emotion_id = data['emotion_id']
            existing.notes = data.get('notes', existing.notes)
            if data.get('photo_url'):
                existing.photo_url = data['photo_url']
            existing.recorded_at = datetime.utcnow()
            entry = existing
        else:
            # 새 기록 생성
            entry = EmotionHistory(
                user_id=current_user.id,
                emotion_id=data['emotion_id'],
                date=record_date,
                notes=data.get('notes'),
                photo_url=data.get('photo_url')
            )
            db.session.add(entry)
        
        db.session.commit()
        return jsonify({
            'message': 'Emotion recorded successfully', 
            'entry': entry.to_dict()
        })
    
    @app.route('/api/emotions/diary/<date_str>', methods=['GET'])
    @login_required
    def get_diary_entry(date_str):
        """특정 날짜의 감정 기록 조회"""
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
        
        entry = EmotionHistory.query.filter_by(
            user_id=current_user.id,
            date=target_date
        ).first()
        
        if entry:
            return jsonify(entry.to_dict())
        return jsonify(None)
    
    @app.route('/api/upload/photo', methods=['POST'])
    @login_required
    def upload_photo():
        """감정 기록용 사진 업로드"""
        if 'photo' not in request.files:
            return jsonify({'error': 'No photo provided'}), 400
        
        file = request.files['photo']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # 안전한 파일명으로 변환
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            
            # 업로드 폴더 생성
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            
            # 파일 저장
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(file_path)
            
            photo_url = f"/api/uploads/{unique_filename}"
            return jsonify({
                'photo_url': photo_url, 
                'filename': unique_filename
            })
        
        return jsonify({'error': 'Invalid file type'}), 400
    
    @app.route('/api/uploads/<filename>')
    def serve_upload(filename):
        """업로드된 파일 서빙"""
        return send_from_directory(UPLOAD_FOLDER, filename)
    
    @app.route('/api/emotions/today', methods=['GET'])
    @login_required
    def get_today_emotion():
        """오늘 기록한 감정 조회"""
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
        """감정 기록 히스토리 조회"""
        days = request.args.get('days', 30, type=int)
        
        history = EmotionHistory.query.filter_by(
            user_id=current_user.id
        ).order_by(
            EmotionHistory.date.desc()
        ).limit(days).all()
        
        return jsonify([h.to_dict() for h in history])
    
    @app.route('/api/emotions/statistics', methods=['GET'])
    @login_required
    def get_emotion_statistics():
        """감정 통계 데이터 조회 (차트용)"""
        days = request.args.get('days', 30, type=int)
        stats = EmotionRecommendationEngine.get_emotion_statistics(
            db, current_user.id, days
        )
        return jsonify(stats)
    
    # ============================================
    # 할일(Task) API
    # ============================================
    
    @app.route('/api/tasks', methods=['GET'])
    @login_required
    def get_tasks():
        """할일 목록 조회 (필터링 지원)"""
        status = request.args.get('status')         # completed / incomplete
        category = request.args.get('category')     # Work / Study / Health / Personal
        date_str = request.args.get('date')         # YYYY-MM-DD
        
        query = Task.query.filter_by(user_id=current_user.id)
        
        # 날짜 필터
        if date_str:
            task_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            query = query.filter_by(task_date=task_date)
        
        # 상태 필터
        if status == 'completed':
            query = query.filter_by(is_completed=True)
        elif status == 'incomplete':
            query = query.filter_by(is_completed=False)
        
        # 카테고리 필터
        if category:
            query = query.filter_by(category=category)
        
        # 최신순 정렬
        tasks = query.order_by(Task.created_at.desc()).all()
        return jsonify([t.to_dict() for t in tasks])
    
    @app.route('/api/tasks', methods=['POST'])
    @login_required
    def create_task():
        """새 할일 생성"""
        data = request.get_json()
        
        if not data or not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400
        
        # 할일 날짜 (없으면 오늘)
        task_date = datetime.now().date()
        if data.get('task_date'):
            task_date = datetime.strptime(data['task_date'], '%Y-%m-%d').date()
        
        # 중복 체크 (같은 날짜에 같은 제목의 미완료 할일)
        existing_task = Task.query.filter_by(
            user_id=current_user.id,
            title=data['title'],
            task_date=task_date,
            is_completed=False
        ).first()
        
        if existing_task:
            return jsonify({
                'error': 'This task already exists for this date', 
                'task': existing_task.to_dict()
            }), 409
        
        # 새 할일 생성
        new_task = Task(
            user_id=current_user.id,
            title=data['title'],
            description=data.get('description'),
            category=data.get('category', 'Personal'),
            priority=data.get('priority', 'Medium'),
            task_date=task_date,
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date() if data.get('due_date') else None,
            recommended_for_emotion=data.get('recommended_for_emotion')
        )
        
        db.session.add(new_task)
        db.session.commit()
        
        return jsonify(new_task.to_dict()), 201
    
    @app.route('/api/tasks/<int:task_id>', methods=['GET'])
    @login_required
    def get_task(task_id):
        """특정 할일 상세 조회"""
        task = Task.query.filter_by(
            id=task_id, 
            user_id=current_user.id
        ).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        return jsonify(task.to_dict())
    
    @app.route('/api/tasks/<int:task_id>', methods=['PUT'])
    @login_required
    def update_task(task_id):
        """할일 수정"""
        task = Task.query.filter_by(
            id=task_id, 
            user_id=current_user.id
        ).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        data = request.get_json()
        
        # 필드별 업데이트
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
            # 완료 처리 시 완료 시간 기록
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
        """할일 삭제"""
        task = Task.query.filter_by(
            id=task_id, 
            user_id=current_user.id
        ).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deleted successfully'})
    
    @app.route('/api/tasks/recommended', methods=['GET'])
    @login_required
    def get_recommended_tasks():
        """현재 감정에 맞는 할일 추천"""
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
        """감정별 새 할일 제안 (할일이 없을 때)"""
        emotion_name = request.args.get('emotion', 'Neutral')
        limit = request.args.get('limit', 3, type=int)
        
        suggestions = EmotionRecommendationEngine.get_suggested_tasks(
            emotion_name, limit
        )
        return jsonify(suggestions)
    
    # ============================================
    # 음악 추천 API
    # ============================================
    
    @app.route('/api/music/recommendations', methods=['GET'])
    def get_music_recommendations():
        """감정에 맞는 음악 추천"""
        emotion_name = request.args.get('emotion', 'Neutral')
        limit = request.args.get('limit', 4, type=int)
        
        user_id = current_user.id if current_user.is_authenticated else None
        
        recommendations = EmotionRecommendationEngine.get_music_recommendations(
            db, emotion_name, user_id, limit
        )
        return jsonify(recommendations)
    
    # ============================================
    # 캘린더 API
    # ============================================
    
    @app.route('/api/calendar/events', methods=['GET'])
    @login_required
    def get_calendar_events():
        """캘린더 일정 조회"""
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        
        query = CalendarEvent.query.filter_by(user_id=current_user.id)
        
        # 월별 필터링
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
        """새 일정 생성"""
        data = request.get_json()
        
        if not data or not data.get('title') or not data.get('start_date'):
            return jsonify({'error': 'Title and start date are required'}), 400
        
        new_event = CalendarEvent(
            user_id=current_user.id,
            title=data['title'],
            description=data.get('description'),
            start_date=datetime.fromisoformat(data['start_date'].replace('Z', '+00:00')),
            end_date=datetime.fromisoformat(data['end_date'].replace('Z', '+00:00')) if data.get('end_date') else None,
            all_day=data.get('all_day', False),
            color=data.get('color', '#6366f1')
        )
        
        db.session.add(new_event)
        db.session.commit()
        
        return jsonify(new_event.to_dict()), 201
    
    @app.route('/api/calendar/events/<int:event_id>', methods=['PUT'])
    @login_required
    def update_calendar_event(event_id):
        """일정 수정"""
        event = CalendarEvent.query.filter_by(
            id=event_id, 
            user_id=current_user.id
        ).first()
        
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
        """일정 삭제"""
        event = CalendarEvent.query.filter_by(
            id=event_id, 
            user_id=current_user.id
        ).first()
        
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        db.session.delete(event)
        db.session.commit()
        return jsonify({'message': 'Event deleted successfully'})
    
    # ============================================
    # 사용자 프로필 API
    # ============================================
    
    @app.route('/api/user/profile', methods=['GET'])
    @login_required
    def get_profile():
        """내 프로필 조회"""
        return jsonify(current_user.to_dict())
    
    @app.route('/api/user/profile', methods=['PUT'])
    @login_required
    def update_profile():
        """프로필 수정"""
        data = request.get_json()
        
        # 사용자명 변경
        if 'username' in data:
            existing = User.query.filter_by(username=data['username']).first()
            if existing and existing.id != current_user.id:
                return jsonify({'error': 'Username already taken'}), 400
            current_user.username = data['username']
        
        # 선호 작업 시간
        if 'preferred_work_time' in data:
            current_user.preferred_work_time = data['preferred_work_time']
        
        # 선호 카테고리
        if 'preferred_categories' in data:
            if isinstance(data['preferred_categories'], list):
                current_user.preferred_categories = ','.join(data['preferred_categories'])
            else:
                current_user.preferred_categories = data['preferred_categories']
        
        # 알림 설정
        if 'notification_enabled' in data:
            current_user.notification_enabled = data['notification_enabled']
        
        db.session.commit()
        return jsonify(current_user.to_dict())
    
    # ============================================
    # 대시보드 API
    # ============================================
    
    @app.route('/api/dashboard/summary', methods=['GET'])
    @login_required
    def get_dashboard_summary():
        """대시보드용 요약 데이터 조회"""
        today = datetime.now().date()
        
        # 오늘의 감정
        today_emotion = EmotionHistory.query.filter_by(
            user_id=current_user.id,
            date=today
        ).first()
        
        # 할일 통계
        total_tasks = Task.query.filter_by(user_id=current_user.id).count()
        completed_tasks = Task.query.filter_by(
            user_id=current_user.id, 
            is_completed=True
        ).count()
        pending_tasks = total_tasks - completed_tasks
        
        # 오늘 마감인 할일들
        today_tasks = Task.query.filter_by(
            user_id=current_user.id,
            due_date=today,
            is_completed=False
        ).all()
        
        # 최근 7일 감정 통계
        weekly_stats = EmotionRecommendationEngine.get_emotion_statistics(
            db, current_user.id, 7
        )
        
        return jsonify({
            'user': current_user.to_dict(),
            'today_emotion': today_emotion.to_dict() if today_emotion else None,
            'task_summary': {
                'total': total_tasks,
                'completed': completed_tasks,
                'pending': pending_tasks
            },
            'today_tasks': [t.to_dict() for t in today_tasks],
            'weekly_mood_stats': weekly_stats
        })
