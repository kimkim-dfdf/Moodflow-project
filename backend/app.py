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
from models import db, User, Quote


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
        
        # Seed demo users if they don't exist
        seed_demo_users()
        
        # Seed quotes if they don't exist
        seed_quotes()
    
    # Register all API routes
    from routes import register_routes
    register_routes(app)
    
    return app


def seed_demo_users():
    """
    Create demo users if they don't exist.
    Only 4 fixed accounts are allowed:
    - seven@gmail.com
    - elly@gmail.com
    - nicole@gmail.com
    - admin@gmail.com
    
    Uses auto-increment IDs (does not hardcode IDs).
    Idempotent - safe to run multiple times.
    """
    
    # List of demo users to create
    # Note: We don't set id, let the database auto-generate it
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
    
    # Check each user and create if not exists
    users_created = False
    
    for user_data in demo_users:
        # Check if user already exists by email
        existing_user = User.query.filter_by(email=user_data['email']).first()
        
        if existing_user is None:
            # Create new user (let database assign ID)
            new_user = User()
            new_user.email = user_data['email']
            new_user.username = user_data['username']
            new_user.password = user_data['password']
            new_user.is_admin = user_data['is_admin']
            db.session.add(new_user)
            print("Created demo user: " + user_data['email'])
            users_created = True
    
    # Save all changes to database
    if users_created:
        db.session.commit()
        print("Demo users seeded successfully.")


def seed_quotes():
    """
    Create quotes if they don't exist.
    Each emotion has multiple motivational quotes.
    Idempotent - safe to run multiple times.
    """
    
    # Check if quotes already exist
    existing_count = Quote.query.count()
    if existing_count > 0:
        return
    
    # List of quotes for each emotion
    quotes_data = [
        # Happy quotes
        {'emotion': 'Happy', 'text': 'Happiness is not something ready made. It comes from your own actions.', 'author': 'Dalai Lama'},
        {'emotion': 'Happy', 'text': 'The purpose of our lives is to be happy.', 'author': 'Dalai Lama'},
        {'emotion': 'Happy', 'text': 'Spread love everywhere you go. Let no one ever come to you without leaving happier.', 'author': 'Mother Teresa'},
        {'emotion': 'Happy', 'text': 'Be so happy that when others look at you, they become happy too.', 'author': 'Yogi Bhajan'},
        {'emotion': 'Happy', 'text': 'Happiness is a direction, not a place.', 'author': 'Sydney J. Harris'},
        
        # Sad quotes
        {'emotion': 'Sad', 'text': 'Every storm runs out of rain. Just like every dark night turns into day.', 'author': 'Gary Allan'},
        {'emotion': 'Sad', 'text': 'The wound is the place where the Light enters you.', 'author': 'Rumi'},
        {'emotion': 'Sad', 'text': 'Tough times never last, but tough people do.', 'author': 'Robert H. Schuller'},
        {'emotion': 'Sad', 'text': 'Even the darkest night will end and the sun will rise.', 'author': 'Victor Hugo'},
        {'emotion': 'Sad', 'text': 'Stars can not shine without darkness.', 'author': 'D.H. Sidebottom'},
        
        # Tired quotes
        {'emotion': 'Tired', 'text': 'Rest when you are weary. Refresh and renew yourself.', 'author': 'Ralph Marston'},
        {'emotion': 'Tired', 'text': 'Almost everything will work again if you unplug it for a few minutes, including you.', 'author': 'Anne Lamott'},
        {'emotion': 'Tired', 'text': 'Take rest; a field that has rested gives a bountiful crop.', 'author': 'Ovid'},
        {'emotion': 'Tired', 'text': 'Your calm mind is the ultimate weapon against your challenges.', 'author': 'Bryant McGill'},
        {'emotion': 'Tired', 'text': 'Sometimes the most productive thing you can do is relax.', 'author': 'Mark Black'},
        
        # Angry quotes
        {'emotion': 'Angry', 'text': 'For every minute you remain angry, you give up sixty seconds of peace of mind.', 'author': 'Ralph Waldo Emerson'},
        {'emotion': 'Angry', 'text': 'Holding on to anger is like grasping a hot coal. You are the one who gets burned.', 'author': 'Buddha'},
        {'emotion': 'Angry', 'text': 'When angry, count to ten before you speak. If very angry, count to one hundred.', 'author': 'Thomas Jefferson'},
        {'emotion': 'Angry', 'text': 'Speak when you are angry and you will make the best speech you will ever regret.', 'author': 'Ambrose Bierce'},
        {'emotion': 'Angry', 'text': 'The best fighter is never angry.', 'author': 'Lao Tzu'},
        
        # Stressed quotes
        {'emotion': 'Stressed', 'text': 'The greatest weapon against stress is our ability to choose one thought over another.', 'author': 'William James'},
        {'emotion': 'Stressed', 'text': 'You don\'t have to control your thoughts. You just have to stop letting them control you.', 'author': 'Dan Millman'},
        {'emotion': 'Stressed', 'text': 'Breathe. Let go. And remind yourself that this very moment is the only one you know you have for sure.', 'author': 'Oprah Winfrey'},
        {'emotion': 'Stressed', 'text': 'Within you, there is a stillness and a sanctuary to which you can retreat at any time.', 'author': 'Hermann Hesse'},
        {'emotion': 'Stressed', 'text': 'It is not stress that kills us, it is our reaction to it.', 'author': 'Hans Selye'},
        
        # Neutral quotes
        {'emotion': 'Neutral', 'text': 'The only way to do great work is to love what you do.', 'author': 'Steve Jobs'},
        {'emotion': 'Neutral', 'text': 'Life is what happens when you are busy making other plans.', 'author': 'John Lennon'},
        {'emotion': 'Neutral', 'text': 'In the middle of difficulty lies opportunity.', 'author': 'Albert Einstein'},
        {'emotion': 'Neutral', 'text': 'The journey of a thousand miles begins with one step.', 'author': 'Lao Tzu'},
        {'emotion': 'Neutral', 'text': 'Do what you can, with what you have, where you are.', 'author': 'Theodore Roosevelt'}
    ]
    
    # Insert all quotes
    for quote_data in quotes_data:
        quote = Quote()
        quote.emotion = quote_data['emotion']
        quote.text = quote_data['text']
        quote.author = quote_data['author']
        db.session.add(quote)
    
    db.session.commit()
    print("Quotes seeded successfully. Total: " + str(len(quotes_data)))
