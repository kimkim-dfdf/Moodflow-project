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
from werkzeug.security import generate_password_hash, check_password_hash


# ==============================================
# Configuration
# ==============================================

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')


# ==============================================
# In-Memory Data Storage
# ==============================================

users = []
tasks = []
emotion_history = []

next_user_id = 1
next_task_id = 1
next_emotion_id = 1


# ==============================================
# File Operations
# ==============================================

def load_data():
    """
    Load all data from the JSON file into memory.
    This is called when the app starts.
    """
    global users, tasks, emotion_history
    global next_user_id, next_task_id, next_emotion_id
    
    # Check if data file exists
    if not os.path.exists(DATA_FILE):
        return
    
    # Read the JSON file
    file = open(DATA_FILE, 'r')
    data = json.load(file)
    file.close()
    
    # Load each data type
    users = data.get('users', [])
    tasks = data.get('tasks', [])
    emotion_history = data.get('emotion_history', [])
    
    # Calculate next IDs based on existing data
    next_user_id = find_max_id(users) + 1
    next_task_id = find_max_id(tasks) + 1
    next_emotion_id = find_max_id(emotion_history) + 1


def save_data():
    """
    Save all data from memory to the JSON file.
    This is called after any data modification.
    """
    data = {
        'users': users,
        'tasks': tasks,
        'emotion_history': emotion_history
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
# User Operations
# ==============================================

def create_user(email, username, password):
    """
    Create a new user account.
    Password is hashed for security.
    """
    global next_user_id
    
    user = {
        'id': next_user_id,
        'email': email,
        'username': username,
        'password_hash': generate_password_hash(password),
        'created_at': datetime.utcnow().isoformat()
    }
    
    users.append(user)
    next_user_id = next_user_id + 1
    save_data()
    
    return user


def get_user_by_id(user_id):
    """Find a user by their ID."""
    for user in users:
        if user['id'] == user_id:
            return user
    return None


def get_user_by_email(email):
    """Find a user by their email address."""
    for user in users:
        if user['email'] == email:
            return user
    return None


def get_user_by_username(username):
    """Find a user by their username."""
    for user in users:
        if user['username'] == username:
            return user
    return None


def check_user_password(user, password):
    """
    Check if the provided password matches the user's password.
    Returns True if password is correct, False otherwise.
    """
    return check_password_hash(user['password_hash'], password)


def update_user(user_id, username):
    """Update a user's username."""
    for user in users:
        if user['id'] == user_id:
            user['username'] = username
            save_data()
            return user
    return None


def user_to_dict(user):
    """
    Convert a user object to a dictionary for API responses.
    Excludes sensitive data like password_hash.
    """
    return {
        'id': user['id'],
        'email': user['email'],
        'username': user['username'],
        'created_at': user['created_at']
    }


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


def get_emotion_history_by_user(user_id, limit):
    """
    Get emotion history for a user.
    Results are sorted by date (newest first).
    """
    result = []
    
    # Filter by user
    for entry in emotion_history:
        if entry['user_id'] == user_id:
            result.append(entry)
    
    # Sort by date (newest first) using bubble sort
    result = bubble_sort_by_date(result, 'date', True)
    
    # Apply limit if specified
    if limit and limit < len(result):
        return result[:limit]
    
    return result


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
