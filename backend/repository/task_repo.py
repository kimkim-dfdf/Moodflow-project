# ==============================================
# Task Repository
# ==============================================
# Handles all task-related database operations
# ==============================================

from datetime import datetime
from models import db, Task


def create_task(user_id, title, category, priority, task_date, recommended_for_emotion):
    """
    Create a new task for a user.
    """
    task = Task()
    task.user_id = user_id
    task.title = title
    task.description = None
    task.category = category
    task.priority = priority
    task.is_completed = False
    task.due_date = None
    task.due_time = None
    task.task_date = task_date
    task.created_at = datetime.utcnow()
    task.completed_at = None
    task.recommended_for_emotion = recommended_for_emotion
    task.emotion_score = 0.0
    
    db.session.add(task)
    db.session.commit()
    
    return task.to_dict()


def get_tasks_by_user(user_id, task_date):
    """
    Get all tasks for a user.
    Optionally filter by task_date.
    Results are sorted by created_at (newest first).
    """
    query = Task.query.filter_by(user_id=user_id)
    
    if task_date:
        query = query.filter_by(task_date=task_date)
    
    query = query.order_by(Task.created_at.desc())
    
    tasks = query.all()
    
    result = []
    for task in tasks:
        result.append(task.to_dict())
    
    return result


def get_incomplete_tasks_by_user(user_id, task_date):
    """
    Get all incomplete tasks for a user.
    Optionally filter by task_date.
    """
    query = Task.query.filter_by(user_id=user_id, is_completed=False)
    
    if task_date:
        query = query.filter_by(task_date=task_date)
    
    tasks = query.all()
    
    result = []
    for task in tasks:
        result.append(task.to_dict())
    
    return result


def get_task_by_id(task_id, user_id):
    """Find a specific task by ID and user ID."""
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if task:
        return task.to_dict()
    return None


def get_existing_task(user_id, title, task_date):
    """
    Check if a task with the same title already exists for this date.
    Used to prevent duplicate tasks.
    """
    task = Task.query.filter_by(
        user_id=user_id,
        title=title,
        task_date=task_date,
        is_completed=False
    ).first()
    
    if task:
        return task.to_dict()
    return None


def update_task(task_id, user_id, is_completed):
    """
    Update a task's completion status.
    Sets completed_at timestamp when completed.
    """
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    
    if task:
        task.is_completed = is_completed
        
        if is_completed:
            task.completed_at = datetime.utcnow()
        else:
            task.completed_at = None
        
        db.session.commit()
        return task.to_dict()
    
    return None


def delete_task(task_id, user_id):
    """
    Delete a task.
    Returns True if deleted, False if not found.
    """
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    
    if task:
        db.session.delete(task)
        db.session.commit()
        return True
    
    return False


def count_tasks(user_id):
    """
    Count total and completed tasks for a user.
    Returns a dictionary with 'total' and 'completed' counts.
    """
    total = Task.query.filter_by(user_id=user_id).count()
    completed = Task.query.filter_by(user_id=user_id, is_completed=True).count()
    
    return {
        'total': total,
        'completed': completed
    }


def get_today_due_tasks(user_id, today):
    """
    Get tasks that are due today and not completed.
    """
    tasks = Task.query.filter_by(
        user_id=user_id,
        due_date=today,
        is_completed=False
    ).all()
    
    result = []
    for task in tasks:
        result.append(task.to_dict())
    
    return result
