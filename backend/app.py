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
from dotenv import load_dotenv
from models import db, User
from seed_data import seed_all_static_data
import repository

# Load environment variables from .env file
load_dotenv()


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
        def seed_demo_users():
            """
            Create demo users if they don't exist.
            Idempotent - safe to run multiple times.
            Passwords are hashed using bcrypt.
            """
            demo_users = [
                {'email': 'seven@gmail.com', 'username': 'Seven', 'password': 'ekdus123', 'is_admin': False},
                {'email': 'elly@gmail.com', 'username': 'Elly', 'password': 'ekdus123', 'is_admin': False},
                {'email': 'nicole@gmail.com', 'username': 'Nicole', 'password': 'ekdus123', 'is_admin': False},
                {'email': 'admin@gmail.com', 'username': 'Admin', 'password': 'ekdus123', 'is_admin': True}
            ]
            
            for user_data in demo_users:
                if User.query.filter_by(email=user_data['email']).first() is None:
                    new_user = User(
                        email=user_data['email'],
                        username=user_data['username'],
                        password=repository.hash_password(user_data['password']),
                        is_admin=user_data['is_admin']
                    )
                    db.session.add(new_user)
                    print("Created demo user: " + user_data['email'])
            
            db.session.commit()
        
        seed_demo_users()
        
        # Seed static data (emotions, music, books, tags)
        seed_all_static_data()
    
    # Register all API routes
    from routes import register_routes
    register_routes(app)
    
    return app
