# -*- coding: utf-8 -*-
"""
MoodFlow 데이터베이스 모델 정의
- 사용자, 감정, 할일, 캘린더, 음악 추천 등 핵심 테이블 구조
- 작성일: 2024년
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


# ============================================
# 사용자 모델 (User)
# - 회원가입, 로그인에 사용되는 사용자 정보
# ============================================
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    # 기본 정보
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)  # 이메일 (로그인용)
    username = db.Column(db.String(80), unique=True, nullable=False)  # 닉네임
    password_hash = db.Column(db.String(256), nullable=False)  # 암호화된 비밀번호
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 가입일
    
    # 사용자 설정값들
    preferred_work_time = db.Column(db.String(20), default='morning')  # 선호 작업 시간대
    preferred_categories = db.Column(db.Text, default='Work,Study,Health,Personal')  # 선호 카테고리
    notification_enabled = db.Column(db.Boolean, default=True)  # 알림 켜기/끄기
    
    # 다른 테이블과의 관계 설정 (1:N)
    tasks = db.relationship('Task', backref='user', lazy=True, cascade='all, delete-orphan')
    emotions = db.relationship('EmotionHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    events = db.relationship('CalendarEvent', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """비밀번호를 암호화해서 저장"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """입력된 비밀번호가 맞는지 확인"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """JSON으로 변환할 때 사용하는 딕셔너리 반환"""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'preferred_work_time': self.preferred_work_time,
            'preferred_categories': self.preferred_categories.split(',') if self.preferred_categories else [],
            'notification_enabled': self.notification_enabled
        }


# ============================================
# 감정 모델 (Emotion)
# - 기본 감정 종류 정의 (Happy, Sad, Angry 등)
# ============================================
class Emotion(db.Model):
    __tablename__ = 'emotions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # 감정 이름 (예: Happy)
    emoji = db.Column(db.String(10), nullable=False)  # 이모지 (예: 😊)
    color = db.Column(db.String(20), nullable=False)  # 색상 코드 (예: #FFD93D)
    energy_level = db.Column(db.Integer, default=5)  # 에너지 레벨 (1~10)
    focus_level = db.Column(db.Integer, default=5)  # 집중력 레벨 (1~10)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'emoji': self.emoji,
            'color': self.color,
            'energy_level': self.energy_level,
            'focus_level': self.focus_level
        }


# ============================================
# 감정 기록 모델 (EmotionHistory)
# - 사용자가 날짜별로 기록한 감정 히스토리
# ============================================
class EmotionHistory(db.Model):
    __tablename__ = 'emotion_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    emotion_id = db.Column(db.Integer, db.ForeignKey('emotions.id'), nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)  # 기록 시간
    date = db.Column(db.Date, nullable=False)  # 해당 날짜
    notes = db.Column(db.Text)  # 메모 (선택사항)
    photo_url = db.Column(db.String(500))  # 사진 URL (선택사항)
    
    # 감정 테이블과 연결
    emotion = db.relationship('Emotion', backref='history_entries')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'emotion_id': self.emotion_id,
            'emotion': self.emotion.to_dict() if self.emotion else None,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
            'date': self.date.isoformat() if self.date else None,
            'notes': self.notes,
            'photo_url': self.photo_url
        }


# ============================================
# 할일 모델 (Task)
# - 사용자가 등록한 할일/태스크 목록
# ============================================
class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 할일 기본 정보
    title = db.Column(db.String(200), nullable=False)  # 제목
    description = db.Column(db.Text)  # 상세 설명
    category = db.Column(db.String(50), default='Personal')  # 카테고리 (Work/Study/Health/Personal)
    priority = db.Column(db.String(20), default='Medium')  # 우선순위 (High/Medium/Low)
    
    # 상태 및 날짜
    is_completed = db.Column(db.Boolean, default=False)  # 완료 여부
    due_date = db.Column(db.Date)  # 마감일
    task_date = db.Column(db.Date, nullable=False)  # 할일 등록 날짜
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)  # 완료한 시간
    
    # 감정 기반 추천 관련
    recommended_for_emotion = db.Column(db.String(50))  # 어떤 감정일 때 추천되었는지
    emotion_score = db.Column(db.Float, default=0.0)  # 추천 점수
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'priority': self.priority,
            'is_completed': self.is_completed,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'task_date': self.task_date.isoformat() if self.task_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'recommended_for_emotion': self.recommended_for_emotion,
            'emotion_score': self.emotion_score
        }


# ============================================
# 캘린더 이벤트 모델 (CalendarEvent)
# - 캘린더에 표시되는 일정들
# ============================================
class CalendarEvent(db.Model):
    __tablename__ = 'calendar_events'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    title = db.Column(db.String(200), nullable=False)  # 일정 제목
    description = db.Column(db.Text)  # 상세 내용
    start_date = db.Column(db.DateTime, nullable=False)  # 시작 시간
    end_date = db.Column(db.DateTime)  # 종료 시간
    all_day = db.Column(db.Boolean, default=False)  # 종일 일정 여부
    color = db.Column(db.String(20), default='#6366f1')  # 표시 색상
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'all_day': self.all_day,
            'color': self.color,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ============================================
# 음악 추천 모델 (MusicRecommendation)
# - 감정별로 추천하는 음악 목록
# ============================================
class MusicRecommendation(db.Model):
    __tablename__ = 'music_recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    emotion_id = db.Column(db.Integer, db.ForeignKey('emotions.id'), nullable=False)
    
    # 음악 정보
    title = db.Column(db.String(200), nullable=False)  # 곡 제목
    artist = db.Column(db.String(100))  # 아티스트
    genre = db.Column(db.String(50))  # 장르
    
    # 외부 링크
    spotify_url = db.Column(db.String(500))  # 스포티파이 링크
    youtube_url = db.Column(db.String(500))  # 유튜브 링크
    thumbnail_url = db.Column(db.String(500))  # 썸네일 이미지
    
    popularity_score = db.Column(db.Float, default=0.0)  # 인기도 점수
    
    # 감정 테이블과 연결
    emotion = db.relationship('Emotion', backref='music_recommendations')
    
    def to_dict(self):
        return {
            'id': self.id,
            'emotion_id': self.emotion_id,
            'emotion': self.emotion.name if self.emotion else None,
            'title': self.title,
            'artist': self.artist,
            'genre': self.genre,
            'spotify_url': self.spotify_url,
            'youtube_url': self.youtube_url,
            'thumbnail_url': self.thumbnail_url,
            'popularity_score': self.popularity_score
        }
