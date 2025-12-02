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
    
    tasks = db.relationship('Task', backref='user', lazy=True, cascade='all, delete-orphan')
    emotions = db.relationship('EmotionHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Emotion(db.Model):
    __tablename__ = 'emotions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    emoji = db.Column(db.String(10), nullable=False)
    color = db.Column(db.String(20), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'emoji': self.emoji,
            'color': self.color
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
    due_time = db.Column(db.String(10))
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
            'due_time': self.due_time,
            'task_date': self.task_date.isoformat() if self.task_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'recommended_for_emotion': self.recommended_for_emotion,
            'emotion_score': self.emotion_score
        }


class MusicRecommendation(db.Model):
    __tablename__ = 'music_recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    emotion_id = db.Column(db.Integer, db.ForeignKey('emotions.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(100))
    genre = db.Column(db.String(50))
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
            'youtube_url': self.youtube_url,
            'thumbnail_url': self.thumbnail_url,
            'popularity_score': self.popularity_score
        }


class BookTag(db.Model):
    __tablename__ = 'book_tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(20), default='#6366f1')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'color': self.color
        }


class BookTagLink(db.Model):
    __tablename__ = 'book_tag_links'
    
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book_recommendations.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('book_tags.id'), nullable=False)
    
    __table_args__ = (db.UniqueConstraint('book_id', 'tag_id', name='unique_book_tag'),)


class BookRecommendation(db.Model):
    __tablename__ = 'book_recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    emotion_id = db.Column(db.Integer, db.ForeignKey('emotions.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100))
    genre = db.Column(db.String(50))
    description = db.Column(db.Text)
    cover_url = db.Column(db.String(500))
    popularity_score = db.Column(db.Float, default=0.0)
    
    emotion = db.relationship('Emotion', backref='book_recommendations')
    tags = db.relationship('BookTag', secondary='book_tag_links', backref='books')
    
    def to_dict(self):
        return {
            'id': self.id,
            'emotion_id': self.emotion_id,
            'emotion': self.emotion.name if self.emotion else None,
            'title': self.title,
            'author': self.author,
            'genre': self.genre,
            'description': self.description,
            'cover_url': self.cover_url,
            'popularity_score': self.popularity_score,
            'tags': [tag.to_dict() for tag in self.tags] if self.tags else []
        }
