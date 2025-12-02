from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
import static_data


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    tasks = db.relationship('Task', backref='user', lazy=True, cascade='all, delete-orphan')
    emotions = db.relationship('EmotionHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        result = {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'created_at': None
        }
        if self.created_at:
            result['created_at'] = self.created_at.isoformat()
        return result


class EmotionHistory(db.Model):
    __tablename__ = 'emotion_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    emotion_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    photo_url = db.Column(db.String(500))
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        emotion = static_data.get_emotion_by_id(self.emotion_id)
        
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'emotion_id': self.emotion_id,
            'emotion': emotion,
            'date': None,
            'notes': self.notes,
            'photo_url': self.photo_url,
            'recorded_at': None
        }
        
        if self.date:
            result['date'] = self.date.isoformat()
        if self.recorded_at:
            result['recorded_at'] = self.recorded_at.isoformat()
        
        return result


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
    due_time = db.Column(db.String(10))
    task_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    recommended_for_emotion = db.Column(db.String(50))
    emotion_score = db.Column(db.Float, default=0.0)
    
    def to_dict(self):
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'priority': self.priority,
            'is_completed': self.is_completed,
            'due_date': None,
            'due_time': self.due_time,
            'task_date': None,
            'created_at': None,
            'completed_at': None,
            'recommended_for_emotion': self.recommended_for_emotion,
            'emotion_score': self.emotion_score
        }
        
        if self.due_date:
            result['due_date'] = self.due_date.isoformat()
        if self.task_date:
            result['task_date'] = self.task_date.isoformat()
        if self.created_at:
            result['created_at'] = self.created_at.isoformat()
        if self.completed_at:
            result['completed_at'] = self.completed_at.isoformat()
        
        return result
