import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')

users = []
tasks = []
emotion_history = []
next_user_id = 1
next_task_id = 1
next_emotion_id = 1


def load_data():
    global users, tasks, emotion_history
    global next_user_id, next_task_id, next_emotion_id
    
    if os.path.exists(DATA_FILE):
        file = open(DATA_FILE, 'r')
        data = json.load(file)
        file.close()
        
        users = data.get('users', [])
        tasks = data.get('tasks', [])
        emotion_history = data.get('emotion_history', [])
        
        if len(users) > 0:
            max_id = 0
            for user in users:
                if user['id'] > max_id:
                    max_id = user['id']
            next_user_id = max_id + 1
        
        if len(tasks) > 0:
            max_id = 0
            for task in tasks:
                if task['id'] > max_id:
                    max_id = task['id']
            next_task_id = max_id + 1
        
        if len(emotion_history) > 0:
            max_id = 0
            for entry in emotion_history:
                if entry['id'] > max_id:
                    max_id = entry['id']
            next_emotion_id = max_id + 1


def save_data():
    data = {
        'users': users,
        'tasks': tasks,
        'emotion_history': emotion_history
    }
    file = open(DATA_FILE, 'w')
    json.dump(data, file, indent=2)
    file.close()


def create_user(email, username, password):
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
    for user in users:
        if user['id'] == user_id:
            return user
    return None


def get_user_by_email(email):
    for user in users:
        if user['email'] == email:
            return user
    return None


def get_user_by_username(username):
    for user in users:
        if user['username'] == username:
            return user
    return None


def check_user_password(user, password):
    return check_password_hash(user['password_hash'], password)


def update_user(user_id, username):
    for user in users:
        if user['id'] == user_id:
            user['username'] = username
            save_data()
            return user
    return None


def user_to_dict(user):
    return {
        'id': user['id'],
        'email': user['email'],
        'username': user['username'],
        'created_at': user['created_at']
    }


def create_task(user_id, title, category, priority, task_date, recommended_for_emotion):
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
    result = []
    for task in tasks:
        if task['user_id'] == user_id:
            if task_date:
                if task['task_date'] == task_date:
                    result.append(task)
            else:
                result.append(task)
    
    for i in range(len(result)):
        for j in range(i + 1, len(result)):
            if result[j]['created_at'] > result[i]['created_at']:
                temp = result[i]
                result[i] = result[j]
                result[j] = temp
    
    return result


def get_incomplete_tasks_by_user(user_id, task_date):
    result = []
    for task in tasks:
        if task['user_id'] == user_id and task['is_completed'] == False:
            if task_date:
                if task['task_date'] == task_date:
                    result.append(task)
            else:
                result.append(task)
    return result


def get_task_by_id(task_id, user_id):
    for task in tasks:
        if task['id'] == task_id and task['user_id'] == user_id:
            return task
    return None


def get_existing_task(user_id, title, task_date):
    for task in tasks:
        if task['user_id'] == user_id and task['title'] == title and task['task_date'] == task_date and task['is_completed'] == False:
            return task
    return None


def update_task(task_id, user_id, is_completed):
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
    global tasks
    for i in range(len(tasks)):
        if tasks[i]['id'] == task_id and tasks[i]['user_id'] == user_id:
            tasks.pop(i)
            save_data()
            return True
    return False


def count_tasks(user_id):
    total = 0
    completed = 0
    for task in tasks:
        if task['user_id'] == user_id:
            total = total + 1
            if task['is_completed']:
                completed = completed + 1
    return {'total': total, 'completed': completed}


def get_today_due_tasks(user_id, today):
    result = []
    for task in tasks:
        if task['user_id'] == user_id and task['due_date'] == today and task['is_completed'] == False:
            result.append(task)
    return result


def create_emotion_entry(user_id, emotion_id, date, notes, photo_url):
    global next_emotion_id
    
    existing = get_emotion_entry_by_date(user_id, date)
    if existing:
        existing['emotion_id'] = emotion_id
        if notes:
            existing['notes'] = notes
        if photo_url:
            existing['photo_url'] = photo_url
        existing['recorded_at'] = datetime.utcnow().isoformat()
        save_data()
        return existing
    
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
    for entry in emotion_history:
        if entry['user_id'] == user_id and entry['date'] == date:
            return entry
    return None


def get_emotion_history_by_user(user_id, limit):
    result = []
    for entry in emotion_history:
        if entry['user_id'] == user_id:
            result.append(entry)
    
    for i in range(len(result)):
        for j in range(i + 1, len(result)):
            if result[j]['date'] > result[i]['date']:
                temp = result[i]
                result[i] = result[j]
                result[j] = temp
    
    if limit and limit < len(result):
        return result[:limit]
    return result


def get_emotion_history_since(user_id, start_date):
    result = []
    for entry in emotion_history:
        if entry['user_id'] == user_id and entry['date'] >= start_date:
            result.append(entry)
    return result


load_data()
