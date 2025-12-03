import os
from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    
    CORS(app, supports_credentials=True, origins=["*"])
    
    secret = os.environ.get("SESSION_SECRET")
    if not secret:
        secret = os.environ.get("FLASK_SECRET_KEY")
    if not secret:
        secret = "dev-secret-key"
    app.secret_key = secret
    
    import repository
    
    from routes import register_routes
    register_routes(app)
    
    return app
