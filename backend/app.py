import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    
    CORS(app, supports_credentials=True, origins=["*"])
    
    secret = os.environ.get("SESSION_SECRET")
    if not secret:
        secret = os.environ.get("FLASK_SECRET_KEY")
    if not secret:
        secret = "dev-secret-key"
    app.secret_key = secret
    
    db_path = os.path.join(os.path.dirname(__file__), 'moodflow.db')
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    db.init_app(app)
    login_manager.init_app(app)
    
    with app.app_context():
        from models import User, EmotionHistory, Task
        
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))
        
        db.create_all()
        
        from routes import register_routes
        register_routes(app, db)
    
    return app
