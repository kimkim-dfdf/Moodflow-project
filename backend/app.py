# ==============================================
# MoodFlow - Flask Application Factory
# ==============================================
# This file creates and configures the Flask app
# Database: PostgreSQL with SQLAlchemy
# ==============================================

import os
import sys
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from models import db, User, Emotion, Music, BookTag, Book


def create_app():
    """
    Create and configure the Flask application.
    This is called the 'Application Factory' pattern.
    """
    
    # Create Flask app
    app = Flask(__name__)
    
    # Enable CORS (Cross-Origin Resource Sharing)
    # This allows the frontend to make requests to the backend
    CORS(app, supports_credentials=True, origins=["*"])
    
    # Set secret key for sessions
    # Try to get from environment variables first
    secret_key = os.environ.get("SESSION_SECRET")
    if not secret_key:
        secret_key = os.environ.get("FLASK_SECRET_KEY")
    if not secret_key:
        secret_key = "moodflow-dev-secret-key-2024"
    
    app.secret_key = secret_key
    
    # ==============================================
    # Database Configuration
    # ==============================================
    
    # Get database URL from environment variable
    database_url = os.environ.get("DATABASE_URL")
    
    # Validate database URL is set
    if not database_url:
        print("ERROR: DATABASE_URL environment variable is not set!")
        print("Please set the DATABASE_URL environment variable to connect to PostgreSQL.")
        print("Example: DATABASE_URL=postgresql://user:password@host:port/database")
        sys.exit(1)
    
    # Configure SQLAlchemy
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # Initialize database with the app
    db.init_app(app)
    
    # ==============================================
    # Flask-Login Configuration
    # ==============================================
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login session management."""
        return db.session.get(User, int(user_id))
    
    # ==============================================
    # Create Database Tables and Seed Data
    # ==============================================
    
    with app.app_context():
        # Create all tables if they don't exist
        db.create_all()
        
        # Seed all initial data
        seed_demo_users()
        seed_emotions()
        seed_book_tags()
        seed_music()
        seed_books()
    
    # Register all API routes
    from routes import register_routes
    register_routes(app)
    
    return app


def seed_demo_users():
    """
    Create demo users if they don't exist.
    Only 4 fixed accounts are allowed.
    Idempotent - safe to run multiple times.
    """
    
    demo_users = [
        {
            'email': 'seven@gmail.com',
            'username': 'Seven',
            'password': 'ekdus123',
            'is_admin': False
        },
        {
            'email': 'elly@gmail.com',
            'username': 'Elly',
            'password': 'ekdus123',
            'is_admin': False
        },
        {
            'email': 'nicole@gmail.com',
            'username': 'Nicole',
            'password': 'ekdus123',
            'is_admin': False
        },
        {
            'email': 'admin@gmail.com',
            'username': 'Admin',
            'password': 'ekdus123',
            'is_admin': True
        }
    ]
    
    users_created = False
    
    for user_data in demo_users:
        existing_user = User.query.filter_by(email=user_data['email']).first()
        
        if existing_user is None:
            new_user = User(
                email=user_data['email'],
                username=user_data['username'],
                password=user_data['password'],
                is_admin=user_data['is_admin']
            )
            db.session.add(new_user)
            print("Created demo user: " + user_data['email'])
            users_created = True
    
    if users_created:
        db.session.commit()
        print("Demo users seeded successfully.")


def seed_emotions():
    """
    Create emotions if they don't exist.
    6 emotions: Happy, Sad, Tired, Angry, Stressed, Neutral
    """
    
    emotions = [
        {'name': 'Happy', 'emoji': '😊', 'color': '#FFD93D'},
        {'name': 'Sad', 'emoji': '😢', 'color': '#6B7FD7'},
        {'name': 'Tired', 'emoji': '😴', 'color': '#8B4513'},
        {'name': 'Angry', 'emoji': '😠', 'color': '#FF6B6B'},
        {'name': 'Stressed', 'emoji': '😰', 'color': '#FF9F43'},
        {'name': 'Neutral', 'emoji': '😐', 'color': '#95A5A6'}
    ]
    
    # Check if emotions already exist
    existing_count = Emotion.query.count()
    if existing_count > 0:
        return
    
    for emotion_data in emotions:
        new_emotion = Emotion(
            name=emotion_data['name'],
            emoji=emotion_data['emoji'],
            color=emotion_data['color']
        )
        db.session.add(new_emotion)
    
    db.session.commit()
    print("Emotions seeded successfully.")


def seed_book_tags():
    """
    Create book tags if they don't exist.
    10 tags with colors.
    """
    
    book_tags = [
        {'name': 'Hopeful', 'slug': 'hopeful', 'color': '#22c55e'},
        {'name': 'Comforting', 'slug': 'comforting', 'color': '#f97316'},
        {'name': 'Peaceful', 'slug': 'peaceful', 'color': '#06b6d4'},
        {'name': 'Growth', 'slug': 'growth', 'color': '#8b5cf6'},
        {'name': 'Emotional', 'slug': 'emotional', 'color': '#ec4899'},
        {'name': 'Escapism', 'slug': 'escapism', 'color': '#6366f1'},
        {'name': 'Recharge', 'slug': 'recharge', 'color': '#14b8a6'},
        {'name': 'Courage', 'slug': 'courage', 'color': '#dc2626'},
        {'name': 'New Perspective', 'slug': 'new-perspective', 'color': '#0d9488'},
        {'name': 'Focus', 'slug': 'focus', 'color': '#3b82f6'}
    ]
    
    # Check if book tags already exist
    existing_count = BookTag.query.count()
    if existing_count > 0:
        return
    
    for tag_data in book_tags:
        new_tag = BookTag(
            name=tag_data['name'],
            slug=tag_data['slug'],
            color=tag_data['color']
        )
        db.session.add(new_tag)
    
    db.session.commit()
    print("Book tags seeded successfully.")


def seed_music():
    """
    Create music recommendations if they don't exist.
    24 songs across 6 emotions.
    """
    
    music_list = [
        # Happy music (4 songs)
        {'emotion': 'Happy', 'title': 'Happy', 'artist': 'Pharrell Williams', 'genre': 'Pop', 'youtube_url': 'https://www.youtube.com/watch?v=ZbZSe6N_BXs'},
        {'emotion': 'Happy', 'title': 'Good as Hell', 'artist': 'Lizzo', 'genre': 'Pop', 'youtube_url': 'https://www.youtube.com/watch?v=SmbmeOgWsqE'},
        {'emotion': 'Happy', 'title': 'Walking on Sunshine', 'artist': 'Katrina and the Waves', 'genre': 'Pop Rock', 'youtube_url': 'https://www.youtube.com/watch?v=iPUmE-tne5U'},
        {'emotion': 'Happy', 'title': 'Uptown Funk', 'artist': 'Bruno Mars', 'genre': 'Funk Pop', 'youtube_url': 'https://www.youtube.com/watch?v=OPf0YbXqDm0'},
        
        # Sad music (4 songs)
        {'emotion': 'Sad', 'title': 'Someone Like You', 'artist': 'Adele', 'genre': 'Pop Ballad', 'youtube_url': 'https://www.youtube.com/watch?v=hLQl3WQQoQ0'},
        {'emotion': 'Sad', 'title': 'Fix You', 'artist': 'Coldplay', 'genre': 'Alternative Rock', 'youtube_url': 'https://www.youtube.com/watch?v=k4V3Mo61fJM'},
        {'emotion': 'Sad', 'title': 'Hurt', 'artist': 'Johnny Cash', 'genre': 'Country', 'youtube_url': 'https://www.youtube.com/watch?v=8AHCfZTRGiI'},
        {'emotion': 'Sad', 'title': 'The Night We Met', 'artist': 'Lord Huron', 'genre': 'Indie Folk', 'youtube_url': 'https://www.youtube.com/watch?v=KtlgYxa6BMU'},
        
        # Tired music (4 songs)
        {'emotion': 'Tired', 'title': 'Weightless', 'artist': 'Marconi Union', 'genre': 'Ambient', 'youtube_url': 'https://www.youtube.com/watch?v=UfcAVejslrU'},
        {'emotion': 'Tired', 'title': 'Clair de Lune', 'artist': 'Debussy', 'genre': 'Classical', 'youtube_url': 'https://www.youtube.com/watch?v=CvFH_6DNRCY'},
        {'emotion': 'Tired', 'title': 'Sunset Lover', 'artist': 'Petit Biscuit', 'genre': 'Electronic', 'youtube_url': 'https://www.youtube.com/watch?v=wuCK-oiE3rM'},
        {'emotion': 'Tired', 'title': 'Sleep', 'artist': 'Max Richter', 'genre': 'Ambient Classical', 'youtube_url': 'https://www.youtube.com/watch?v=4UAqmSJhN9M'},
        
        # Angry music (4 songs)
        {'emotion': 'Angry', 'title': 'Break Stuff', 'artist': 'Limp Bizkit', 'genre': 'Nu Metal', 'youtube_url': 'https://www.youtube.com/watch?v=ZpUYjpKg9KY'},
        {'emotion': 'Angry', 'title': 'Killing in the Name', 'artist': 'Rage Against the Machine', 'genre': 'Rock', 'youtube_url': 'https://www.youtube.com/watch?v=bWXazVhlyxQ'},
        {'emotion': 'Angry', 'title': 'Bodies', 'artist': 'Drowning Pool', 'genre': 'Metal', 'youtube_url': 'https://www.youtube.com/watch?v=04F4xlWSFh0'},
        {'emotion': 'Angry', 'title': 'Chop Suey!', 'artist': 'System of a Down', 'genre': 'Metal', 'youtube_url': 'https://www.youtube.com/watch?v=CSvFpBOe8eY'},
        
        # Stressed music (4 songs)
        {'emotion': 'Stressed', 'title': 'Breathe Me', 'artist': 'Sia', 'genre': 'Pop', 'youtube_url': 'https://www.youtube.com/watch?v=wHOH3VMHVx8'},
        {'emotion': 'Stressed', 'title': 'Orinoco Flow', 'artist': 'Enya', 'genre': 'New Age', 'youtube_url': 'https://www.youtube.com/watch?v=LTrk4X9ACtw'},
        {'emotion': 'Stressed', 'title': 'Ocean Eyes', 'artist': 'Billie Eilish', 'genre': 'Electropop', 'youtube_url': 'https://www.youtube.com/watch?v=viimfQi_pUw'},
        {'emotion': 'Stressed', 'title': 'Strawberry Swing', 'artist': 'Coldplay', 'genre': 'Alternative Rock', 'youtube_url': 'https://www.youtube.com/watch?v=h3pJZSTQqIg'},
        
        # Neutral music (4 songs)
        {'emotion': 'Neutral', 'title': 'Lovely Day', 'artist': 'Bill Withers', 'genre': 'Soul', 'youtube_url': 'https://www.youtube.com/watch?v=bEeaS6fuUoA'},
        {'emotion': 'Neutral', 'title': 'Here Comes the Sun', 'artist': 'The Beatles', 'genre': 'Rock', 'youtube_url': 'https://www.youtube.com/watch?v=KQetemT1sWc'},
        {'emotion': 'Neutral', 'title': 'Budapest', 'artist': 'George Ezra', 'genre': 'Folk Pop', 'youtube_url': 'https://www.youtube.com/watch?v=VHrLPs3_1Fs'},
        {'emotion': 'Neutral', 'title': 'Electric Feel', 'artist': 'MGMT', 'genre': 'Indie Electronic', 'youtube_url': 'https://www.youtube.com/watch?v=MmZexg8sxyk'}
    ]
    
    # Check if music already exists
    existing_count = Music.query.count()
    if existing_count > 0:
        return
    
    for music_data in music_list:
        new_music = Music(
            emotion=music_data['emotion'],
            title=music_data['title'],
            artist=music_data['artist'],
            genre=music_data['genre'],
            youtube_url=music_data['youtube_url'],
            is_custom=False
        )
        db.session.add(new_music)
    
    db.session.commit()
    print("Music seeded successfully. (24 songs)")


def seed_books():
    """
    Create book recommendations if they don't exist.
    15 books across different emotions.
    """
    
    book_list = [
        # Happy books (4)
        {'emotion': 'Happy', 'title': 'The Alchemist', 'author': 'Paulo Coelho', 'genre': 'Fiction', 'description': 'A magical story about following your dreams', 'tags': 'hopeful,growth,new-perspective'},
        {'emotion': 'Happy', 'title': 'Big Magic', 'author': 'Elizabeth Gilbert', 'genre': 'Self-Help', 'description': 'Creative living beyond fear', 'tags': 'growth,focus,hopeful'},
        {'emotion': 'Happy', 'title': 'The Happiness Project', 'author': 'Gretchen Rubin', 'genre': 'Self-Help', 'description': 'A year-long journey to discover happiness', 'tags': 'hopeful,growth,recharge'},
        {'emotion': 'Happy', 'title': 'Yes Please', 'author': 'Amy Poehler', 'genre': 'Memoir', 'description': 'Hilarious and inspiring stories', 'tags': 'hopeful,courage,emotional'},
        
        # Sad books (4)
        {'emotion': 'Sad', 'title': 'When Breath Becomes Air', 'author': 'Paul Kalanithi', 'genre': 'Memoir', 'description': 'A profound reflection on life and death', 'tags': 'emotional,comforting,growth'},
        {'emotion': 'Sad', 'title': 'The Year of Magical Thinking', 'author': 'Joan Didion', 'genre': 'Memoir', 'description': 'Processing grief and loss', 'tags': 'comforting,emotional,peaceful'},
        {'emotion': 'Sad', 'title': 'Tiny Beautiful Things', 'author': 'Cheryl Strayed', 'genre': 'Self-Help', 'description': 'Advice on life and love', 'tags': 'comforting,emotional,peaceful'},
        {'emotion': 'Sad', 'title': 'Norwegian Wood', 'author': 'Haruki Murakami', 'genre': 'Fiction', 'description': 'A story of love and melancholy', 'tags': 'emotional,escapism,peaceful'},
        
        # Tired books (4)
        {'emotion': 'Tired', 'title': 'The Little Prince', 'author': 'Antoine de Saint-Exupery', 'genre': 'Fiction', 'description': 'A gentle tale with deep meaning', 'tags': 'hopeful,escapism,new-perspective'},
        {'emotion': 'Tired', 'title': 'Winnie-the-Pooh', 'author': 'A.A. Milne', 'genre': 'Fiction', 'description': 'Comforting adventures in the Hundred Acre Wood', 'tags': 'comforting,recharge,peaceful'},
        {'emotion': 'Tired', 'title': 'The House in the Cerulean Sea', 'author': 'TJ Klune', 'genre': 'Fantasy', 'description': 'A cozy, heartwarming fantasy', 'tags': 'escapism,comforting,peaceful'},
        {'emotion': 'Tired', 'title': 'Hygge: The Danish Art of Living', 'author': 'Meik Wiking', 'genre': 'Lifestyle', 'description': 'Finding comfort in simple pleasures', 'tags': 'recharge,peaceful,comforting'},
        
        # Angry books (3)
        {'emotion': 'Angry', 'title': 'The Art of War', 'author': 'Sun Tzu', 'genre': 'Philosophy', 'description': 'Ancient wisdom on strategy', 'tags': 'courage,focus,growth'},
        {'emotion': 'Angry', 'title': 'Rage', 'author': 'Bob Woodward', 'genre': 'Non-Fiction', 'description': 'Understanding power and politics', 'tags': 'emotional,courage,comforting'},
        {'emotion': 'Angry', 'title': 'Anger: Wisdom for Cooling the Flames', 'author': 'Thich Nhat Hanh', 'genre': 'Self-Help', 'description': 'Buddhist approach to managing anger', 'tags': 'peaceful,new-perspective,growth'}
    ]
    
    # Check if books already exists
    existing_count = Book.query.count()
    if existing_count > 0:
        return
    
    for book_data in book_list:
        new_book = Book(
            emotion=book_data['emotion'],
            title=book_data['title'],
            author=book_data['author'],
            genre=book_data['genre'],
            description=book_data['description'],
            tags=book_data['tags'],
            is_custom=False
        )
        db.session.add(new_book)
    
    db.session.commit()
    print("Books seeded successfully. (15 books)")
