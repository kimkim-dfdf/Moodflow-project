# ==============================================
# MoodFlow - Database Models (Simplified)
# ==============================================
# This file defines the database tables
# Using SQLAlchemy ORM with PostgreSQL
# ==============================================

import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import DeclarativeBase


# ==============================================
# Database Setup
# ==============================================

class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


db = SQLAlchemy(model_class=Base)


# ==============================================
# User Model
# ==============================================

class User(UserMixin, db.Model):
    """
    User table for storing user accounts.
    Inherits from UserMixin for Flask-Login integration.
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    
    def get_id(self):
        """Return user ID as string for Flask-Login."""
        return str(self.id)
    
    def to_dict(self):
        """Convert user to dictionary for API responses."""
        result = {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_admin': self.is_admin
        }
        return result


# ==============================================
# Task Model
# ==============================================

class Task(db.Model):
    """
    Task table for storing user tasks.
    Each task belongs to a user.
    """
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(20), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    task_date = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    recommended_for_emotion = db.Column(db.String(50), nullable=True)
    
    def to_dict(self):
        """Convert task to dictionary for API responses."""
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'category': self.category,
            'priority': self.priority,
            'is_completed': self.is_completed,
            'task_date': self.task_date,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'recommended_for_emotion': self.recommended_for_emotion
        }
        return result


# ==============================================
# Emotion History Model
# ==============================================

class EmotionHistory(db.Model):
    """
    EmotionHistory table for storing daily emotion records.
    Each record belongs to a user and has a specific date.
    """
    __tablename__ = 'emotion_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    emotion_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    photo_url = db.Column(db.String(500), nullable=True)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert emotion entry to dictionary for API responses."""
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'emotion_id': self.emotion_id,
            'date': self.date,
            'notes': self.notes,
            'photo_url': self.photo_url,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None
        }
        return result


# ==============================================
# Emotion Model
# ==============================================

class Emotion(db.Model):
    """
    Emotion table for storing emotion types.
    Contains predefined emotions with their visual properties.
    """
    __tablename__ = 'emotions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    emoji = db.Column(db.String(10), nullable=False)
    color = db.Column(db.String(20), nullable=False)
    
    def to_dict(self):
        """Convert emotion to dictionary for API responses."""
        result = {
            'id': self.id,
            'name': self.name,
            'emoji': self.emoji,
            'color': self.color
        }
        return result


# ==============================================
# Music Model
# ==============================================

class Music(db.Model):
    """
    Music table for storing music recommendations.
    Each music is linked to an emotion.
    """
    __tablename__ = 'music'
    
    id = db.Column(db.Integer, primary_key=True)
    emotion = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    youtube_url = db.Column(db.String(500), nullable=False)
    
    def __init__(self, emotion=None, title=None, artist=None, genre=None, youtube_url=None):
        """Initialize a Music object."""
        self.emotion = emotion
        self.title = title
        self.artist = artist
        self.genre = genre
        self.youtube_url = youtube_url
    
    def to_dict(self):
        """Convert music to dictionary for API responses."""
        result = {
            'id': self.id,
            'emotion': self.emotion,
            'title': self.title,
            'artist': self.artist,
            'genre': self.genre,
            'youtube_url': self.youtube_url
        }
        return result


# ==============================================
# Book Tag Model
# ==============================================

class BookTag(db.Model):
    """
    BookTag table for storing book tags.
    Used for filtering books by tag.
    """
    __tablename__ = 'book_tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(20), nullable=False)
    
    def to_dict(self):
        """Convert tag to dictionary for API responses."""
        result = {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'color': self.color
        }
        return result


# ==============================================
# Book Model
# ==============================================

class Book(db.Model):
    """
    Book table for storing book recommendations.
    Each book is linked to an emotion and has multiple tags.
    """
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    emotion = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    tags = db.Column(db.String(500), nullable=False)
    
    def __init__(self, emotion=None, title=None, author=None, genre=None, description=None, tags=None):
        """Initialize a Book object."""
        self.emotion = emotion
        self.title = title
        self.author = author
        self.genre = genre
        self.description = description
        self.tags = tags
    
    def to_dict(self):
        """Convert book to dictionary for API responses."""
        result = {
            'id': self.id,
            'emotion': self.emotion,
            'title': self.title,
            'author': self.author,
            'genre': self.genre,
            'description': self.description,
            'tags': self.tags.split(',') if self.tags else []
        }
        return result


# ==============================================
# Book Review Model
# ==============================================

class BookReview(db.Model):
    """
    BookReview table for storing user book reviews.
    Each review belongs to a user and a book.
    """
    __tablename__ = 'book_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    book_id = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert review to dictionary for API responses."""
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'rating': self.rating,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        return result


# ==============================================
# Music Review Model
# ==============================================

class MusicReview(db.Model):
    """
    MusicReview table for storing user music reviews.
    Each review belongs to a user and a music track.
    No rating - just text content.
    """
    __tablename__ = 'music_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    music_id = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert review to dictionary for API responses."""
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'music_id': self.music_id,
            'rating': self.rating,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        return result


# ==============================================
# Music Listening Tag Model
# ==============================================

class MusicListeningTag(db.Model):
    """
    MusicListeningTag table for storing predefined listening mood tags.
    Examples: "Good for studying", "Workout", "Relaxing", etc.
    """
    __tablename__ = 'music_listening_tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    emoji = db.Column(db.String(10), nullable=False)
    
    def to_dict(self):
        """Convert tag to dictionary for API responses."""
        result = {
            'id': self.id,
            'name': self.name,
            'emoji': self.emoji
        }
        return result


# ==============================================
# User Music Tag Model
# ==============================================

class UserMusicTag(db.Model):
    """
    UserMusicTag table for storing user-music-tag associations.
    Links users to music with specific listening tags.
    """
    __tablename__ = 'user_music_tags'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    music_id = db.Column(db.Integer, nullable=False)
    tag_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'music_id': self.music_id,
            'tag_id': self.tag_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        return result
