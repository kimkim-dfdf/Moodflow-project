# ==============================================
# User Repository
# ==============================================
# Handles all user-related database operations
# ==============================================

from models import db, User


def get_user_by_id(user_id):
    """Find a user by their ID and return User object."""
    user = db.session.get(User, int(user_id))
    return user


def get_user_by_email(email):
    """Find a user by their email address and return User object."""
    user = User.query.filter_by(email=email).first()
    return user


def check_user_password(user, password):
    """
    Check if the provided password is correct.
    Simple string comparison (no hashing for demo).
    """
    if user.password == password:
        return True
    return False


def user_to_dict(user):
    """
    Convert a user object to a dictionary for API responses.
    Excludes password from the response.
    """
    return user.to_dict()


def get_user_by_username(username):
    """Find a user by their username and return User object."""
    user = User.query.filter_by(username=username).first()
    return user


def update_user(user_id, new_username):
    """
    Update a user's username.
    """
    user = db.session.get(User, int(user_id))
    if user:
        user.username = new_username
        db.session.commit()
        return user
    return None
