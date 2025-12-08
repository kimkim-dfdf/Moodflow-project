# ==============================================
# MoodFlow - Flask Application Factory
# ==============================================

import os
import sys
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from models import db, User, Quote


# ==============================================
# Seed Data (Demo Users)
# ==============================================

DEMO_USERS = [
    {'email': 'seven@gmail.com', 'username': 'Seven', 'password': 'ekdus123', 'is_admin': False},
    {'email': 'elly@gmail.com', 'username': 'Elly', 'password': 'ekdus123', 'is_admin': False},
    {'email': 'nicole@gmail.com', 'username': 'Nicole', 'password': 'ekdus123', 'is_admin': False},
    {'email': 'admin@gmail.com', 'username': 'Admin', 'password': 'ekdus123', 'is_admin': True}
]


# ==============================================
# Seed Data (Quotes)
# ==============================================

QUOTES_DATA = [
    {'emotion': 'Happy', 'text': 'Happiness is not something ready made. It comes from your own actions.', 'author': 'Dalai Lama'},
    {'emotion': 'Happy', 'text': 'The purpose of our lives is to be happy.', 'author': 'Dalai Lama'},
    {'emotion': 'Happy', 'text': 'Spread love everywhere you go. Let no one ever come to you without leaving happier.', 'author': 'Mother Teresa'},
    {'emotion': 'Happy', 'text': 'Be so happy that when others look at you, they become happy too.', 'author': 'Yogi Bhajan'},
    {'emotion': 'Happy', 'text': 'Happiness is a direction, not a place.', 'author': 'Sydney J. Harris'},
    {'emotion': 'Sad', 'text': 'Every storm runs out of rain. Just like every dark night turns into day.', 'author': 'Gary Allan'},
    {'emotion': 'Sad', 'text': 'The wound is the place where the Light enters you.', 'author': 'Rumi'},
    {'emotion': 'Sad', 'text': 'Tough times never last, but tough people do.', 'author': 'Robert H. Schuller'},
    {'emotion': 'Sad', 'text': 'Even the darkest night will end and the sun will rise.', 'author': 'Victor Hugo'},
    {'emotion': 'Sad', 'text': 'Stars can not shine without darkness.', 'author': 'D.H. Sidebottom'},
    {'emotion': 'Tired', 'text': 'Rest when you are weary. Refresh and renew yourself.', 'author': 'Ralph Marston'},
    {'emotion': 'Tired', 'text': 'Almost everything will work again if you unplug it for a few minutes, including you.', 'author': 'Anne Lamott'},
    {'emotion': 'Tired', 'text': 'Take rest; a field that has rested gives a bountiful crop.', 'author': 'Ovid'},
    {'emotion': 'Tired', 'text': 'Your calm mind is the ultimate weapon against your challenges.', 'author': 'Bryant McGill'},
    {'emotion': 'Tired', 'text': 'Sometimes the most productive thing you can do is relax.', 'author': 'Mark Black'},
    {'emotion': 'Angry', 'text': 'For every minute you remain angry, you give up sixty seconds of peace of mind.', 'author': 'Ralph Waldo Emerson'},
    {'emotion': 'Angry', 'text': 'Holding on to anger is like grasping a hot coal. You are the one who gets burned.', 'author': 'Buddha'},
    {'emotion': 'Angry', 'text': 'When angry, count to ten before you speak. If very angry, count to one hundred.', 'author': 'Thomas Jefferson'},
    {'emotion': 'Angry', 'text': 'Speak when you are angry and you will make the best speech you will ever regret.', 'author': 'Ambrose Bierce'},
    {'emotion': 'Angry', 'text': 'The best fighter is never angry.', 'author': 'Lao Tzu'},
    {'emotion': 'Stressed', 'text': 'The greatest weapon against stress is our ability to choose one thought over another.', 'author': 'William James'},
    {'emotion': 'Stressed', 'text': 'You don\'t have to control your thoughts. You just have to stop letting them control you.', 'author': 'Dan Millman'},
    {'emotion': 'Stressed', 'text': 'Breathe. Let go. And remind yourself that this very moment is the only one you know you have for sure.', 'author': 'Oprah Winfrey'},
    {'emotion': 'Stressed', 'text': 'Within you, there is a stillness and a sanctuary to which you can retreat at any time.', 'author': 'Hermann Hesse'},
    {'emotion': 'Stressed', 'text': 'It is not stress that kills us, it is our reaction to it.', 'author': 'Hans Selye'},
    {'emotion': 'Neutral', 'text': 'The only way to do great work is to love what you do.', 'author': 'Steve Jobs'},
    {'emotion': 'Neutral', 'text': 'Life is what happens when you are busy making other plans.', 'author': 'John Lennon'},
    {'emotion': 'Neutral', 'text': 'In the middle of difficulty lies opportunity.', 'author': 'Albert Einstein'},
    {'emotion': 'Neutral', 'text': 'The journey of a thousand miles begins with one step.', 'author': 'Lao Tzu'},
    {'emotion': 'Neutral', 'text': 'Do what you can, with what you have, where you are.', 'author': 'Theodore Roosevelt'}
]


# ==============================================
# Application Factory
# ==============================================

def create_app():
    """Create and configure the Flask application."""
    
    app = Flask(__name__)
    
    # CORS configuration
    CORS(app, supports_credentials=True, origins=["*"])
    
    # Secret key configuration
    secret_key = os.environ.get("SESSION_SECRET")
    if not secret_key:
        secret_key = os.environ.get("FLASK_SECRET_KEY")
    if not secret_key:
        secret_key = "moodflow-dev-secret-key-2024"
    app.secret_key = secret_key
    
    # Database configuration
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable is not set!")
        sys.exit(1)
    
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Initialize database
    db.init_app(app)
    
    # Flask-Login configuration
    login_manager = LoginManager()
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    # Create tables and seed data
    with app.app_context():
        db.create_all()
        seed_demo_users()
        seed_quotes()
    
    # Register routes
    from routes import register_routes
    register_routes(app)
    
    return app


# ==============================================
# Seed Functions
# ==============================================

def seed_demo_users():
    """Create demo users if they don't exist."""
    users_created = False
    
    for user_data in DEMO_USERS:
        existing = User.query.filter_by(email=user_data['email']).first()
        if existing is None:
            new_user = User()
            new_user.email = user_data['email']
            new_user.username = user_data['username']
            new_user.password = user_data['password']
            new_user.is_admin = user_data['is_admin']
            db.session.add(new_user)
            users_created = True
    
    if users_created:
        db.session.commit()


def seed_quotes():
    """Create quotes if they don't exist."""
    if Quote.query.count() > 0:
        return
    
    for quote_data in QUOTES_DATA:
        quote = Quote()
        quote.emotion = quote_data['emotion']
        quote.text = quote_data['text']
        quote.author = quote_data['author']
        db.session.add(quote)
    
    db.session.commit()
