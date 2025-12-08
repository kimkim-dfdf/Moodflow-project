# ==============================================
# MoodFlow - Database Models (Production)
# ==============================================
# ForeignKey, Relationship, Date/DateTime, Many-to-Many
# ==============================================

from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import ForeignKey, Index


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


# ==============================================
# Association Table: Book <-> BookTag (Many-to-Many)
# ==============================================

book_tag_association = db.Table(
    'book_tag_association',
    db.Column('book_id', db.Integer, ForeignKey('books.id', ondelete='CASCADE'), primary_key=True),
    db.Column('tag_id', db.Integer, ForeignKey('book_tags.id', ondelete='CASCADE'), primary_key=True)
)


# ==============================================
# User Model
# ==============================================

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    tasks = relationship('Task', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    emotion_history = relationship('EmotionHistory', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    book_favorites = relationship('BookFavorite', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    music_favorites = relationship('MusicFavorite', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_id(self):
        return str(self.id)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ==============================================
# Emotion Model
# ==============================================

class Emotion(db.Model):
    __tablename__ = 'emotions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    emoji = db.Column(db.String(10), nullable=False)
    color = db.Column(db.String(20), nullable=False)
    
    emotion_history = relationship('EmotionHistory', back_populates='emotion', lazy='dynamic')
    tasks = relationship('Task', back_populates='emotion', lazy='dynamic')
    music_list = relationship('Music', back_populates='emotion', lazy='dynamic')
    books = relationship('Book', back_populates='emotion', lazy='dynamic')
    quotes = relationship('Quote', back_populates='emotion', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'emoji': self.emoji,
            'color': self.color
        }


# ==============================================
# Task Model
# ==============================================

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    emotion_id = db.Column(db.Integer, ForeignKey('emotions.id', ondelete='SET NULL'), nullable=True, index=True)
    
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(20), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    emotion_score = db.Column(db.Float, default=0.0)
    
    task_date = db.Column(db.Date, nullable=True, index=True)
    due_date = db.Column(db.Date, nullable=True)
    due_time = db.Column(db.Time, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    user = relationship('User', back_populates='tasks')
    emotion = relationship('Emotion', back_populates='tasks')
    
    __table_args__ = (
        Index('idx_task_user_date', 'user_id', 'task_date'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'priority': self.priority,
            'is_completed': self.is_completed,
            'task_date': self.task_date.isoformat() if self.task_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'due_time': self.due_time.isoformat() if self.due_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'recommended_for_emotion': self.emotion.name if self.emotion else None,
            'emotion_score': self.emotion_score
        }


# ==============================================
# EmotionHistory Model
# ==============================================

class EmotionHistory(db.Model):
    __tablename__ = 'emotion_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    emotion_id = db.Column(db.Integer, ForeignKey('emotions.id', ondelete='CASCADE'), nullable=False, index=True)
    
    date = db.Column(db.Date, nullable=False, index=True)
    notes = db.Column(db.Text, nullable=True)
    photo_url = db.Column(db.String(500), nullable=True)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = relationship('User', back_populates='emotion_history')
    emotion = relationship('Emotion', back_populates='emotion_history')
    
    __table_args__ = (
        Index('idx_emotion_user_date', 'user_id', 'date', unique=True),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'emotion_id': self.emotion_id,
            'emotion': self.emotion.to_dict() if self.emotion else None,
            'date': self.date.isoformat() if self.date else None,
            'notes': self.notes,
            'photo_url': self.photo_url,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None
        }


# ==============================================
# BookTag Model
# ==============================================

class BookTag(db.Model):
    __tablename__ = 'book_tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False, index=True)
    color = db.Column(db.String(20), nullable=False)
    
    books = relationship('Book', secondary=book_tag_association, back_populates='tags')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'color': self.color
        }


# ==============================================
# Book Model
# ==============================================

class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    emotion_id = db.Column(db.Integer, ForeignKey('emotions.id', ondelete='CASCADE'), nullable=False, index=True)
    
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    emotion = relationship('Emotion', back_populates='books')
    tags = relationship('BookTag', secondary=book_tag_association, back_populates='books')
    favorites = relationship('BookFavorite', back_populates='book', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'emotion': self.emotion.name if self.emotion else None,
            'title': self.title,
            'author': self.author,
            'genre': self.genre,
            'description': self.description,
            'tags': [tag.to_dict() for tag in self.tags]
        }


# ==============================================
# BookFavorite Model
# ==============================================

class BookFavorite(db.Model):
    __tablename__ = 'book_favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    book_id = db.Column(db.Integer, ForeignKey('books.id', ondelete='CASCADE'), nullable=False, index=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = relationship('User', back_populates='book_favorites')
    book = relationship('Book', back_populates='favorites')
    
    __table_args__ = (
        Index('idx_book_fav_unique', 'user_id', 'book_id', unique=True),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'book': self.book.to_dict() if self.book else None,
            'added_at': self.added_at.isoformat() if self.added_at else None
        }


# ==============================================
# Music Model
# ==============================================

class Music(db.Model):
    __tablename__ = 'music'
    
    id = db.Column(db.Integer, primary_key=True)
    emotion_id = db.Column(db.Integer, ForeignKey('emotions.id', ondelete='CASCADE'), nullable=False, index=True)
    
    title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    youtube_url = db.Column(db.String(500), nullable=False)
    
    emotion = relationship('Emotion', back_populates='music_list')
    favorites = relationship('MusicFavorite', back_populates='music', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'emotion': self.emotion.name if self.emotion else None,
            'title': self.title,
            'artist': self.artist,
            'genre': self.genre,
            'youtube_url': self.youtube_url
        }


# ==============================================
# MusicFavorite Model
# ==============================================

class MusicFavorite(db.Model):
    __tablename__ = 'music_favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    music_id = db.Column(db.Integer, ForeignKey('music.id', ondelete='CASCADE'), nullable=False, index=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = relationship('User', back_populates='music_favorites')
    music = relationship('Music', back_populates='favorites')
    
    __table_args__ = (
        Index('idx_music_fav_unique', 'user_id', 'music_id', unique=True),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'music_id': self.music_id,
            'music': self.music.to_dict() if self.music else None,
            'added_at': self.added_at.isoformat() if self.added_at else None
        }


# ==============================================
# Quote Model
# ==============================================

class Quote(db.Model):
    __tablename__ = 'quotes'
    
    id = db.Column(db.Integer, primary_key=True)
    emotion_id = db.Column(db.Integer, ForeignKey('emotions.id', ondelete='CASCADE'), nullable=False, index=True)
    
    text = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(200), nullable=False)
    
    emotion = relationship('Emotion', back_populates='quotes')
    
    def to_dict(self):
        return {
            'id': self.id,
            'emotion': self.emotion.name if self.emotion else None,
            'text': self.text,
            'author': self.author
        }
