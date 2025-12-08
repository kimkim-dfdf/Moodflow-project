# ==============================================
# MoodFlow - Data Repository
# ==============================================
# This file handles all data storage operations
# Data is stored in a JSON file (data.json)
# No database required!
# ==============================================

import json
import os
from datetime import datetime
from flask_login import UserMixin


# ==============================================
# Configuration
# ==============================================

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')


# ==============================================
# User Class for Flask-Login
# ==============================================

class User(UserMixin):
    """User class for Flask-Login integration."""
    
    def __init__(self, user_data):
        self.id = user_data['id']
        self.email = user_data['email']
        self.username = user_data['username']
        self.password = user_data['password']
        self.created_at = user_data['created_at']
        self.is_admin = user_data.get('is_admin', False)
    
    def get_id(self):
        """Return user ID as string for Flask-Login."""
        return str(self.id)
    
    def to_dict(self):
        """Convert user to dictionary for API responses."""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'created_at': self.created_at,
            'is_admin': self.is_admin
        }


# ==============================================
# Demo Users (Fixed Accounts)
# ==============================================
# Only these 3 users can log in
# Password is the same for all: ekdus123

DEMO_USERS = [
    {
        'id': 1,
        'email': 'seven@gmail.com',
        'username': 'Seven',
        'password': 'ekdus123',
        'created_at': '2024-01-01T00:00:00',
        'is_admin': False
    },
    {
        'id': 2,
        'email': 'elly@gmail.com',
        'username': 'Elly',
        'password': 'ekdus123',
        'created_at': '2024-01-01T00:00:00',
        'is_admin': False
    },
    {
        'id': 3,
        'email': 'nicole@gmail.com',
        'username': 'Nicole',
        'password': 'ekdus123',
        'created_at': '2024-01-01T00:00:00',
        'is_admin': False
    },
    {
        'id': 4,
        'email': 'admin@gmail.com',
        'username': 'Admin',
        'password': 'ekdus123',
        'created_at': '2024-01-01T00:00:00',
        'is_admin': True
    }
]


# ==============================================
# In-Memory Data Storage
# ==============================================

tasks = []
emotion_history = []
custom_music = []
custom_books = []
book_favorites = []

next_task_id = 1
next_emotion_id = 1
next_music_id = 100
next_book_id = 100


# ==============================================
# File Operations
# ==============================================

def load_data():
    """
    Load all data from the JSON file into memory.
    This is called when the app starts.
    """
    global tasks, emotion_history, custom_music, custom_books, book_favorites
    global next_task_id, next_emotion_id, next_music_id, next_book_id
    
    # Check if data file exists
    if not os.path.exists(DATA_FILE):
        return
    
    # Read the JSON file
    file = open(DATA_FILE, 'r')
    data = json.load(file)
    file.close()
    
    # Load each data type
    tasks = data.get('tasks', [])
    emotion_history = data.get('emotion_history', [])
    custom_music = data.get('custom_music', [])
    custom_books = data.get('custom_books', [])
    book_favorites = data.get('book_favorites', [])
    
    # Calculate next IDs based on existing data
    next_task_id = find_max_id(tasks) + 1
    next_emotion_id = find_max_id(emotion_history) + 1
    next_music_id = max(find_max_id(custom_music) + 1, 100)
    next_book_id = max(find_max_id(custom_books) + 1, 100)


def save_data():
    """
    Save all data from memory to the JSON file.
    This is called after any data modification.
    """
    data = {
        'tasks': tasks,
        'emotion_history': emotion_history,
        'custom_music': custom_music,
        'custom_books': custom_books,
        'book_favorites': book_favorites
    }
    
    file = open(DATA_FILE, 'w')
    json.dump(data, file, indent=2)
    file.close()


def find_max_id(items):
    """
    Find the maximum ID in a list of items.
    Used to calculate the next ID for new items.
    """
    if len(items) == 0:
        return 0
    
    max_id = 0
    for item in items:
        if item['id'] > max_id:
            max_id = item['id']
    
    return max_id


# ==============================================
# User Operations (Simplified)
# ==============================================

def get_user_by_id(user_id):
    """Find a demo user by their ID and return User object."""
    for user_data in DEMO_USERS:
        if user_data['id'] == int(user_id):
            return User(user_data)
    return None


def get_user_by_email(email):
    """Find a demo user by their email address and return User object."""
    for user_data in DEMO_USERS:
        if user_data['email'] == email:
            return User(user_data)
    return None


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
    """Find a demo user by their username and return User object."""
    for user_data in DEMO_USERS:
        if user_data['username'] == username:
            return User(user_data)
    return None


def update_user(user_id, new_username):
    """
    Update a demo user's username.
    Changes the username in the DEMO_USERS list.
    """
    for user_data in DEMO_USERS:
        if user_data['id'] == user_id:
            user_data['username'] = new_username
            return User(user_data)
    return None


# ==============================================
# Task Operations
# ==============================================

def create_task(user_id, title, category, priority, task_date, recommended_for_emotion):
    """
    Create a new task for a user.
    """
    global next_task_id
    
    task = {
        'id': next_task_id,
        'user_id': user_id,
        'title': title,
        'description': None,
        'category': category,
        'priority': priority,
        'is_completed': False,
        'due_date': None,
        'due_time': None,
        'task_date': task_date,
        'created_at': datetime.utcnow().isoformat(),
        'completed_at': None,
        'recommended_for_emotion': recommended_for_emotion,
        'emotion_score': 0.0
    }
    
    tasks.append(task)
    next_task_id = next_task_id + 1
    save_data()
    
    return task


def get_tasks_by_user(user_id, task_date):
    """
    Get all tasks for a user.
    Optionally filter by task_date.
    Results are sorted by created_at (newest first).
    """
    result = []
    
    # Filter tasks by user and optionally by date
    for task in tasks:
        if task['user_id'] != user_id:
            continue
        
        if task_date:
            if task['task_date'] == task_date:
                result.append(task)
        else:
            result.append(task)
    
    # Sort by created_at (newest first) using bubble sort
    result = bubble_sort_by_date(result, 'created_at', True)
    
    return result


def get_incomplete_tasks_by_user(user_id, task_date):
    """
    Get all incomplete tasks for a user.
    Optionally filter by task_date.
    """
    result = []
    
    for task in tasks:
        # Skip if not this user's task
        if task['user_id'] != user_id:
            continue
        
        # Skip if task is completed
        if task['is_completed'] == True:
            continue
        
        # Filter by date if provided
        if task_date:
            if task['task_date'] == task_date:
                result.append(task)
        else:
            result.append(task)
    
    return result


def get_task_by_id(task_id, user_id):
    """Find a specific task by ID and user ID."""
    for task in tasks:
        if task['id'] == task_id and task['user_id'] == user_id:
            return task
    return None


def get_existing_task(user_id, title, task_date):
    """
    Check if a task with the same title already exists for this date.
    Used to prevent duplicate tasks.
    """
    for task in tasks:
        is_same_user = task['user_id'] == user_id
        is_same_title = task['title'] == title
        is_same_date = task['task_date'] == task_date
        is_not_completed = task['is_completed'] == False
        
        if is_same_user and is_same_title and is_same_date and is_not_completed:
            return task
    
    return None


def update_task(task_id, user_id, is_completed):
    """
    Update a task's completion status.
    Sets completed_at timestamp when completed.
    """
    for task in tasks:
        if task['id'] == task_id and task['user_id'] == user_id:
            task['is_completed'] = is_completed
            
            if is_completed:
                task['completed_at'] = datetime.utcnow().isoformat()
            else:
                task['completed_at'] = None
            
            save_data()
            return task
    
    return None


def delete_task(task_id, user_id):
    """
    Delete a task.
    Returns True if deleted, False if not found.
    """
    global tasks
    
    for i in range(len(tasks)):
        if tasks[i]['id'] == task_id and tasks[i]['user_id'] == user_id:
            tasks.pop(i)
            save_data()
            return True
    
    return False


def count_tasks(user_id):
    """
    Count total and completed tasks for a user.
    Returns a dictionary with 'total' and 'completed' counts.
    """
    total = 0
    completed = 0
    
    for task in tasks:
        if task['user_id'] == user_id:
            total = total + 1
            if task['is_completed']:
                completed = completed + 1
    
    return {
        'total': total,
        'completed': completed
    }


def get_today_due_tasks(user_id, today):
    """
    Get tasks that are due today and not completed.
    """
    result = []
    
    for task in tasks:
        is_users_task = task['user_id'] == user_id
        is_due_today = task['due_date'] == today
        is_not_completed = task['is_completed'] == False
        
        if is_users_task and is_due_today and is_not_completed:
            result.append(task)
    
    return result


# ==============================================
# Emotion History Operations
# ==============================================

def create_emotion_entry(user_id, emotion_id, date, notes, photo_url):
    """
    Create or update an emotion entry for a specific date.
    If an entry already exists for this date, update it.
    """
    global next_emotion_id
    
    # Check if entry already exists for this date
    existing = get_emotion_entry_by_date(user_id, date)
    
    if existing:
        # Update existing entry
        existing['emotion_id'] = emotion_id
        existing['recorded_at'] = datetime.utcnow().isoformat()
        
        if notes:
            existing['notes'] = notes
        if photo_url:
            existing['photo_url'] = photo_url
        
        save_data()
        return existing
    
    # Create new entry
    entry = {
        'id': next_emotion_id,
        'user_id': user_id,
        'emotion_id': emotion_id,
        'date': date,
        'notes': notes,
        'photo_url': photo_url,
        'recorded_at': datetime.utcnow().isoformat()
    }
    
    emotion_history.append(entry)
    next_emotion_id = next_emotion_id + 1
    save_data()
    
    return entry


def get_emotion_entry_by_date(user_id, date):
    """Find an emotion entry for a specific date."""
    for entry in emotion_history:
        if entry['user_id'] == user_id and entry['date'] == date:
            return entry
    return None


def get_emotion_history_since(user_id, start_date):
    """
    Get emotion entries since a specific date.
    Used for calculating statistics.
    """
    result = []
    
    for entry in emotion_history:
        is_users_entry = entry['user_id'] == user_id
        is_after_start = entry['date'] >= start_date
        
        if is_users_entry and is_after_start:
            result.append(entry)
    
    return result


# ==============================================
# Music Operations (Admin)
# ==============================================

def get_all_custom_music():
    """Get all custom music entries."""
    return custom_music


def create_music(emotion, title, artist, genre, youtube_url):
    """Create a new music recommendation."""
    global next_music_id
    
    music = {
        'id': next_music_id,
        'emotion': emotion,
        'title': title,
        'artist': artist,
        'genre': genre,
        'youtube_url': youtube_url,
        'is_custom': True
    }
    
    custom_music.append(music)
    next_music_id = next_music_id + 1
    save_data()
    
    return music


def update_music(music_id, emotion, title, artist, genre, youtube_url):
    """Update an existing custom music entry."""
    for music in custom_music:
        if music['id'] == music_id:
            music['emotion'] = emotion
            music['title'] = title
            music['artist'] = artist
            music['genre'] = genre
            music['youtube_url'] = youtube_url
            save_data()
            return music
    return None


def delete_music(music_id):
    """Delete a custom music entry."""
    global custom_music
    
    for i in range(len(custom_music)):
        if custom_music[i]['id'] == music_id:
            custom_music.pop(i)
            save_data()
            return True
    return False


# ==============================================
# Book Operations (Admin)
# ==============================================

def get_all_custom_books():
    """Get all custom book entries."""
    return custom_books


def create_book(emotion, title, author, genre, description, tags):
    """Create a new book recommendation."""
    global next_book_id
    
    book = {
        'id': next_book_id,
        'emotion': emotion,
        'title': title,
        'author': author,
        'genre': genre,
        'description': description,
        'tags': tags,
        'is_custom': True
    }
    
    custom_books.append(book)
    next_book_id = next_book_id + 1
    save_data()
    
    return book


def update_book(book_id, emotion, title, author, genre, description, tags):
    """Update an existing custom book entry."""
    for book in custom_books:
        if book['id'] == book_id:
            book['emotion'] = emotion
            book['title'] = title
            book['author'] = author
            book['genre'] = genre
            book['description'] = description
            book['tags'] = tags
            save_data()
            return book
    return None


def delete_book(book_id):
    """Delete a custom book entry."""
    global custom_books
    
    for i in range(len(custom_books)):
        if custom_books[i]['id'] == book_id:
            custom_books.pop(i)
            save_data()
            return True
    return False


# ==============================================
# Admin Statistics Operations
# ==============================================

def get_all_users_stats():
    """Get statistics for all users."""
    stats = []
    
    for user_data in DEMO_USERS:
        if user_data.get('is_admin'):
            continue
        
        user_id = user_data['id']
        task_counts = count_tasks(user_id)
        emotion_count = 0
        
        for entry in emotion_history:
            if entry['user_id'] == user_id:
                emotion_count = emotion_count + 1
        
        stats.append({
            'user_id': user_id,
            'username': user_data['username'],
            'email': user_data['email'],
            'total_tasks': task_counts['total'],
            'completed_tasks': task_counts['completed'],
            'emotion_entries': emotion_count
        })
    
    return stats


def get_overall_emotion_stats():
    """Get overall emotion statistics across all users."""
    emotion_counts = {}
    
    for entry in emotion_history:
        emotion_id = entry['emotion_id']
        if emotion_id in emotion_counts:
            emotion_counts[emotion_id] = emotion_counts[emotion_id] + 1
        else:
            emotion_counts[emotion_id] = 1
    
    return emotion_counts


def get_overall_task_stats():
    """Get overall task statistics across all users."""
    total = len(tasks)
    completed = 0
    category_counts = {}
    
    for task in tasks:
        if task['is_completed']:
            completed = completed + 1
        
        category = task['category']
        if category in category_counts:
            category_counts[category] = category_counts[category] + 1
        else:
            category_counts[category] = 1
    
    return {
        'total': total,
        'completed': completed,
        'pending': total - completed,
        'by_category': category_counts
    }


# ==============================================
# Utility Functions
# ==============================================

def bubble_sort_by_date(items, date_field, descending):
    """
    Sort a list of items by a date field using bubble sort.
    If descending is True, newest items come first.
    """
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            should_swap = False
            
            if descending:
                # Swap if j's date is greater (newer)
                if items[j][date_field] > items[i][date_field]:
                    should_swap = True
            else:
                # Swap if j's date is smaller (older)
                if items[j][date_field] < items[i][date_field]:
                    should_swap = True
            
            if should_swap:
                temp = items[i]
                items[i] = items[j]
                items[j] = temp
    
    return items


# ==============================================
# Book Favorites Operations
# ==============================================

def get_user_favorites(user_id):
    """
    Get all favorite book IDs for a user.
    Returns a list of book IDs.
    """
    result = []
    
    for favorite in book_favorites:
        if favorite['user_id'] == user_id:
            result.append(favorite['book_id'])
    
    return result


def add_favorite(user_id, book_id):
    """
    Add a book to user's favorites.
    Returns True if added, False if already exists.
    """
    # Check if already in favorites
    for favorite in book_favorites:
        if favorite['user_id'] == user_id and favorite['book_id'] == book_id:
            return False
    
    # Add new favorite
    favorite = {
        'user_id': user_id,
        'book_id': book_id,
        'added_at': datetime.utcnow().isoformat()
    }
    
    book_favorites.append(favorite)
    save_data()
    
    return True


def remove_favorite(user_id, book_id):
    """
    Remove a book from user's favorites.
    Returns True if removed, False if not found.
    """
    global book_favorites
    
    for i in range(len(book_favorites)):
        if book_favorites[i]['user_id'] == user_id and book_favorites[i]['book_id'] == book_id:
            book_favorites.pop(i)
            save_data()
            return True
    
    return False


def is_favorite(user_id, book_id):
    """
    Check if a book is in user's favorites.
    Returns True if favorite, False otherwise.
    """
    for favorite in book_favorites:
        if favorite['user_id'] == user_id and favorite['book_id'] == book_id:
            return True
    
    return False
