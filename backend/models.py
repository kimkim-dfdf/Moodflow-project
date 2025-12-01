from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    preferred_work_time = db.Column(db.String(20), default='morning')
    preferred_categories = db.Column(db.Text, default='Work,Study,Health,Personal')
    notification_enabled = db.Column(db.Boolean, default=True)
    
    tasks = db.relationship('Task', backref='user', lazy=True, cascade='all, delete-orphan')
    emotions = db.relationship('EmotionHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    events = db.relationship('CalendarEvent', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'preferred_work_time': self.preferred_work_time,
            'preferred_categories': self.preferred_categories.split(',') if self.preferred_categories else [],
            'notification_enabled': self.notification_enabled
        }


class Emotion(db.Model):
    __tablename__ = 'emotions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    emoji = db.Column(db.String(10), nullable=False)
    color = db.Column(db.String(20), nullable=False)
    energy_level = db.Column(db.Integer, default=5)
    focus_level = db.Column(db.Integer, default=5)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'emoji': self.emoji,
            'color': self.color,
            'energy_level': self.energy_level,
            'focus_level': self.focus_level
        }


class EmotionHistory(db.Model):
    __tablename__ = 'emotion_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    emotion_id = db.Column(db.Integer, db.ForeignKey('emotions.id'), nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    photo_url = db.Column(db.String(500))
    
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


class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), default='Personal')
    priority = db.Column(db.String(20), default='Medium')
    is_completed = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.Date)
    task_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    recommended_for_emotion = db.Column(db.String(50))
    emotion_score = db.Column(db.Float, default=0.0)
    
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


class CalendarEvent(db.Model):
    __tablename__ = 'calendar_events'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    all_day = db.Column(db.Boolean, default=False)
    color = db.Column(db.String(20), default='#6366f1')
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


class MusicRecommendation(db.Model):
    __tablename__ = 'music_recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    emotion_id = db.Column(db.Integer, db.ForeignKey('emotions.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(100))
    genre = db.Column(db.String(50))
    spotify_url = db.Column(db.String(500))
    youtube_url = db.Column(db.String(500))
    thumbnail_url = db.Column(db.String(500))
    popularity_score = db.Column(db.Float, default=0.0)
    
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
