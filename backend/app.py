# ==============================================
# MoodFlow - Flask Application Factory
# ==============================================
# This file creates and configures the Flask app
# ==============================================

import os
from flask import Flask
from flask_cors import CORS


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
    
    # Initialize the data repository
    # This loads any existing data from the JSON file
    import repository
    repository.load_data()
    
    # Register all API routes
    from routes import register_routes
    register_routes(app)
    
    return app
