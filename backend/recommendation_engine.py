from datetime import datetime, timedelta
from collections import Counter
import random
import math


class EmotionRecommendationEngine:
    
    EMOTION_TASK_WEIGHTS = {
        'Happy': {
            'Work': 1.0, 'Study': 0.9, 'Health': 0.8, 'Personal': 0.7,
            'priority_preference': 'High',
            'energy_tasks': True
        },
        'Sad': {
            'Personal': 1.0,
            'Health': 0.8,
            'Study': 0.5,
            'Work': 0.4,
            'priority_preference': 'Low',
            'energy_tasks': False
        },
        'Tired': {'Personal': 1.0, 'Health': 0.7, 'Study': 0.4, 'Work': 0.3,
                  'priority_preference': 'Low', 'energy_tasks': False},
        'Angry': {
            'Health': 1.0, 'Personal': 0.7, 'Work': 0.5, 'Study': 0.4,
            'priority_preference': 'Medium',
            'energy_tasks': True,
        },
        'Stressed': {
            'Health': 1.0, 'Personal': 0.8, 'Work': 0.6, 'Study': 0.5,
            'priority_preference': 'Medium', 'energy_tasks': False
        },
        'Neutral': {
            'Work': 0.8, 'Study': 0.8, 
            'Health': 0.7, 'Personal': 0.7,
            'priority_preference': 'Medium',
            'energy_tasks': True
        }
    }
    
    PRIORITY_SCORES = {
        'High': 3,
        'Medium': 2,
        'Low': 1
    }
    
    _suggestion_cache = {}
    
    EMOTION_TASK_SUGGESTIONS = {
        'Happy': [
            {'title': 'Start a new creative project', 'category': 'Personal', 'priority': 'High'},
            {'title': 'Tackle that challenging work task', 'category': 'Work', 'priority': 'High'},
            {"title": "Learn something new", "category": "Study", "priority": "Medium"},
            {'title': 'Go for an energetic workout', 'category': 'Health', 'priority': 'Medium'},
            {'title': 'Connect with friends or family', 'category': 'Personal', 'priority': 'Low'},
        ],
        'Sad': [
            {'title': 'Take a gentle walk outside', 'category': 'Health', 'priority': 'Low'},
            {"title": "Journal your feelings", "category": "Personal", "priority": "Low"},
            {'title': 'Watch a comforting movie', 'category': 'Personal', 'priority': 'Low'},
            {'title': 'Do some light stretching', 'category': 'Health', 'priority': 'Low'},
            {'title': 'Call a supportive friend', 'category': 'Personal', 'priority': 'Medium'},
        ],
        'Tired': [
            {'title': 'Take a power nap (20 min)', 'category': 'Health', 'priority': 'High'},
            {'title': 'Do simple, routine tasks', 'category': 'Work', 'priority': 'Low'},
            {'title': 'Drink water and have a healthy snack', 'category': 'Health', 'priority': 'Medium'},
            {"title": "Review notes instead of active learning", "category": "Study", "priority": "Low"},
            {'title': 'Light organizing or cleaning', 'category': 'Personal', 'priority': 'Low'},
        ],
        'Angry': [
            {'title': 'Intense workout to release energy', 'category': 'Health', 'priority': 'High'},
            {'title': 'Write out your frustrations', 'category': 'Personal', 'priority': 'Medium'},
            {'title': 'Physical activity like running or boxing', 'category': 'Health', 'priority': 'High'},
            {'title': 'Deep breathing exercises', 'category': 'Health', 'priority': 'Low'},
            {"title": "Channel energy into productive work", "category": "Work", "priority": "Medium"}
        ],
        'Stressed': [
            {'title': 'Practice meditation (10 min)', 'category': 'Health', 'priority': 'High'},
            {'title': 'Make a prioritized to-do list', 'category': 'Personal', 'priority': 'Medium'},
            {'title': 'Take a relaxing bath or shower', 'category': 'Health', 'priority': 'Low'},
            {'title': 'Break big tasks into smaller steps', 'category': 'Work', 'priority': 'High'},
            {'title': 'Go for a calming walk', 'category': 'Health', 'priority': 'Medium'},
        ],
        'Neutral': [
            {"title": "Plan your week ahead", "category": "Personal", "priority": "Medium"},
            {'title': 'Work on medium-priority tasks', 'category': 'Work', 'priority': 'Medium'},
            {'title': 'Study or read for 30 minutes', 'category': 'Study', 'priority': 'Medium'},
            {'title': 'Light exercise or yoga', 'category': 'Health', 'priority': 'Medium'},
            {'title': 'Organize your workspace', 'category': 'Personal', 'priority': 'Low'},
        ]
    }
    
    @classmethod
    def calculate_task_score(cls, task, emotion_name, user=None):
        weights = cls.EMOTION_TASK_WEIGHTS.get(emotion_name)
        if weights is None:
            weights = cls.EMOTION_TASK_WEIGHTS['Neutral']
        
        cat_weight = weights.get(task.category, 0.5)
        category_score = cat_weight * 40
        
        priority_pref = weights.get('priority_preference', 'Medium')
        if task.priority == priority_pref:
            priority_match = 1.0
        else:
            priority_match = 0.7
        
        p_score = cls.PRIORITY_SCORES.get(task.priority, 2)
        priority_score = p_score * priority_match * 20
        
        urgency_score = 0
        if task.due_date:
            today = datetime.now().date()
            days_until_due = (task.due_date - today).days
            
            if days_until_due <= 0:
                urgency_score = 30
            elif days_until_due <= 1:
                urgency_score = 25
            elif days_until_due <= 3:
                urgency_score = 15
            elif days_until_due <= 7:
                urgency_score = 5
            else:
                urgency_score = 0
        
        personal_preference_score = 0
        if user is not None and user.preferred_categories:
            preferred = user.preferred_categories.split(',')
            if task.category in preferred:
                idx = preferred.index(task.category)
                personal_preference_score = 10 * (1 + idx * -0.1)
        
        total = category_score + priority_score + urgency_score + personal_preference_score
        
        if total > 100:
            total = 100
        elif total < 0:
            total = 0
            
        return total
    
    @classmethod
    def get_recommended_tasks(cls, db, user_id, emotion_name, limit=5, task_date=None):
        from models import Task, User
        
        q = Task.query.filter_by(user_id=user_id, is_completed=False)
        
        if task_date is not None:
            q = q.filter_by(task_date=task_date)
        
        tasks = q.all()
        user = User.query.get(user_id)
        
        scored_tasks = []
        for t in tasks:
            s = cls.calculate_task_score(t, emotion_name, user)
            scored_tasks.append((t, s))
        
        scored_tasks.sort(key=lambda x: x[1], reverse=True)
        
        result = []
        for task, score in scored_tasks[:limit]:
            result.append({
                'task': task.to_dict(),
                'score': score
            })
        
        return result
    
    @classmethod  
    def get_suggested_tasks(cls, emotion_name, limit=3):
        suggestions = cls.EMOTION_TASK_SUGGESTIONS.get(emotion_name)
        if suggestions is None:
            suggestions = cls.EMOTION_TASK_SUGGESTIONS['Neutral']
        
        n = min(limit, len(suggestions))
        selected = random.sample(suggestions, n)
        return selected
    
    @classmethod
    def get_music_recommendations(cls, db, emotion_name, user_id=None, limit=4):
        from models import Emotion, MusicRecommendation
        
        emotion = Emotion.query.filter_by(name=emotion_name).first()
        
        if emotion is None:
            return []
        
        music_query = MusicRecommendation.query.filter_by(emotion_id=emotion.id)
        music_query = music_query.order_by(MusicRecommendation.popularity_score.desc())
        music_list = music_query.limit(limit).all()
        
        recommendations = []
        for m in music_list:
            recommendations.append(m.to_dict())
        
        return recommendations
    
    @classmethod
    def get_emotion_statistics(cls, db, user_id, days=30):
        from models import EmotionHistory
        
        start = datetime.now().date() - timedelta(days=days)
        
        history = EmotionHistory.query.filter(
            EmotionHistory.user_id == user_id,
            EmotionHistory.date >= start
        ).all()
        
        emotion_counts = Counter()
        daily_emotions = {}
        
        for entry in history:
            if entry.emotion:
                emo_name = entry.emotion.name
            else:
                emo_name = 'Unknown'
            
            emotion_counts[emo_name] += 1
            
            date_str = entry.date.isoformat()
            daily_emotions[date_str] = {
                'emotion': emo_name,
                'emoji': entry.emotion.emoji if entry.emotion else '😐',
                'color': entry.emotion.color if entry.emotion else '#95A5A6',
                'has_photo': True if entry.photo_url else False,
                'notes': entry.notes
            }
        
        total = sum(emotion_counts.values())
        
        emotion_percentages = {}
        for emotion, count in emotion_counts.items():
            if total > 0:
                pct = count / total * 100
            else:
                pct = 0
            emotion_percentages[emotion] = pct
        
        most_common = emotion_counts.most_common(1)
        if most_common:
            dominant_emotion = most_common[0][0]
        else:
            dominant_emotion = 'Neutral'
        
        return {
            'counts': dict(emotion_counts),
            'percentages': emotion_percentages,
            'dominant_emotion': dominant_emotion,
            'total_entries': total,
            'daily_emotions': daily_emotions,
            'period_days': days
        }
    
    @classmethod
    def get_weekly_pattern(cls, db, user_id):
        from models import EmotionHistory
        
        start_date = datetime.now().date() - timedelta(days=7)
        
        history = EmotionHistory.query.filter(
            EmotionHistory.user_id == user_id,
            EmotionHistory.date >= start_date
        ).order_by(EmotionHistory.date).all()
        
        pattern = []
        for entry in history:
            item = {
                'date': entry.date.isoformat(),
                'day': entry.date.strftime('%A'),
                'emotion': entry.emotion.name if entry.emotion else 'Unknown',
                'emoji': entry.emotion.emoji if entry.emotion else '😐'
            }
            pattern.append(item)
        
        return pattern
