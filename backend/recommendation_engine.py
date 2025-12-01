from datetime import datetime, timedelta
from collections import Counter
import random


class EmotionRecommendationEngine:
    
    EMOTION_TASK_WEIGHTS = {
        'Happy': {
            'Work': 1.0, 'Study': 0.9, 'Health': 0.8, 'Personal': 0.7,
            'priority_preference': 'High',
            'energy_tasks': True
        },
        'Sad': {
            'Personal': 1.0, 'Health': 0.8, 'Study': 0.5, 'Work': 0.4,
            'priority_preference': 'Low',
            'energy_tasks': False
        },
        'Tired': {
            'Personal': 1.0, 'Health': 0.7, 'Study': 0.4, 'Work': 0.3,
            'priority_preference': 'Low',
            'energy_tasks': False
        },
        'Angry': {
            'Health': 1.0, 'Personal': 0.7, 'Work': 0.5, 'Study': 0.4,
            'priority_preference': 'Medium',
            'energy_tasks': True
        },
        'Stressed': {
            'Health': 1.0, 'Personal': 0.8, 'Work': 0.6, 'Study': 0.5,
            'priority_preference': 'Medium',
            'energy_tasks': False
        },
        'Neutral': {
            'Work': 0.8, 'Study': 0.8, 'Health': 0.7, 'Personal': 0.7,
            'priority_preference': 'Medium',
            'energy_tasks': True
        }
    }
    
    PRIORITY_SCORES = {'High': 3, 'Medium': 2, 'Low': 1}
    
    EMOTION_TASK_SUGGESTIONS = {
        'Happy': [
            {'title': 'Start a new creative project', 'category': 'Personal', 'priority': 'High'},
            {'title': 'Tackle that challenging work task', 'category': 'Work', 'priority': 'High'},
            {'title': 'Learn something new', 'category': 'Study', 'priority': 'Medium'},
            {'title': 'Go for an energetic workout', 'category': 'Health', 'priority': 'Medium'},
            {'title': 'Connect with friends or family', 'category': 'Personal', 'priority': 'Low'},
        ],
        'Sad': [
            {'title': 'Take a gentle walk outside', 'category': 'Health', 'priority': 'Low'},
            {'title': 'Journal your feelings', 'category': 'Personal', 'priority': 'Low'},
            {'title': 'Watch a comforting movie', 'category': 'Personal', 'priority': 'Low'},
            {'title': 'Do some light stretching', 'category': 'Health', 'priority': 'Low'},
            {'title': 'Call a supportive friend', 'category': 'Personal', 'priority': 'Medium'},
        ],
        'Tired': [
            {'title': 'Take a power nap (20 min)', 'category': 'Health', 'priority': 'High'},
            {'title': 'Do simple, routine tasks', 'category': 'Work', 'priority': 'Low'},
            {'title': 'Drink water and have a healthy snack', 'category': 'Health', 'priority': 'Medium'},
            {'title': 'Review notes instead of active learning', 'category': 'Study', 'priority': 'Low'},
            {'title': 'Light organizing or cleaning', 'category': 'Personal', 'priority': 'Low'},
        ],
        'Angry': [
            {'title': 'Intense workout to release energy', 'category': 'Health', 'priority': 'High'},
            {'title': 'Write out your frustrations', 'category': 'Personal', 'priority': 'Medium'},
            {'title': 'Physical activity like running or boxing', 'category': 'Health', 'priority': 'High'},
            {'title': 'Deep breathing exercises', 'category': 'Health', 'priority': 'Low'},
            {'title': 'Channel energy into productive work', 'category': 'Work', 'priority': 'Medium'},
        ],
        'Stressed': [
            {'title': 'Practice meditation (10 min)', 'category': 'Health', 'priority': 'High'},
            {'title': 'Make a prioritized to-do list', 'category': 'Personal', 'priority': 'Medium'},
            {'title': 'Take a relaxing bath or shower', 'category': 'Health', 'priority': 'Low'},
            {'title': 'Break big tasks into smaller steps', 'category': 'Work', 'priority': 'High'},
            {'title': 'Go for a calming walk', 'category': 'Health', 'priority': 'Medium'},
        ],
        'Neutral': [
            {'title': 'Plan your week ahead', 'category': 'Personal', 'priority': 'Medium'},
            {'title': 'Work on medium-priority tasks', 'category': 'Work', 'priority': 'Medium'},
            {'title': 'Study or read for 30 minutes', 'category': 'Study', 'priority': 'Medium'},
            {'title': 'Light exercise or yoga', 'category': 'Health', 'priority': 'Medium'},
            {'title': 'Organize your workspace', 'category': 'Personal', 'priority': 'Low'},
        ]
    }
    
    @classmethod
    def calculate_task_score(cls, task, emotion_name, user=None):
        weights = cls.EMOTION_TASK_WEIGHTS.get(emotion_name, cls.EMOTION_TASK_WEIGHTS['Neutral'])
        
        category_weight = weights.get(task.category, 0.5)
        priority_pref = weights.get('priority_preference', 'Medium')
        priority_weight = cls.PRIORITY_SCORES.get(task.priority, 2) / 3.0
        
        priority_match = 1.0 if task.priority == priority_pref else 0.6
        
        urgency_weight = 0
        if task.due_date:
            days_until_due = (task.due_date - datetime.now().date()).days
            if days_until_due <= 0:
                urgency_weight = 1.0
            elif days_until_due <= 1:
                urgency_weight = 0.9
            elif days_until_due <= 3:
                urgency_weight = 0.6
            elif days_until_due <= 7:
                urgency_weight = 0.3
        
        weighted_score = (
            category_weight * 50 +
            priority_weight * priority_match * 30 +
            urgency_weight * 20
        )
        
        return min(100, max(0, weighted_score))
    
    @classmethod
    def get_recommended_tasks(cls, db, user_id, emotion_name, limit=5):
        from models import Task, User
        
        tasks = Task.query.filter_by(
            user_id=user_id,
            is_completed=False
        ).all()
        
        user = User.query.get(user_id)
        
        scored_tasks = []
        for task in tasks:
            score = cls.calculate_task_score(task, emotion_name, user)
            scored_tasks.append((task, score))
        
        scored_tasks.sort(key=lambda x: x[1], reverse=True)
        
        return [{'task': task.to_dict(), 'score': score} for task, score in scored_tasks[:limit]]
    
    @classmethod
    def get_suggested_tasks(cls, emotion_name, limit=3):
        suggestions = cls.EMOTION_TASK_SUGGESTIONS.get(emotion_name, cls.EMOTION_TASK_SUGGESTIONS['Neutral'])
        weights = cls.EMOTION_TASK_WEIGHTS.get(emotion_name, cls.EMOTION_TASK_WEIGHTS['Neutral'])
        
        def suggestion_score(suggestion):
            cat_weight = weights.get(suggestion['category'], 0.5)
            priority_pref = weights.get('priority_preference', 'Medium')
            priority_match = 1.0 if suggestion['priority'] == priority_pref else 0.7
            return cat_weight * 50 + cls.PRIORITY_SCORES.get(suggestion['priority'], 2) * priority_match * 20
        
        scored_suggestions = [(s, suggestion_score(s)) for s in suggestions]
        scored_suggestions.sort(key=lambda x: x[1], reverse=True)
        
        return [s[0] for s in scored_suggestions[:limit]]
    
    @classmethod
    def get_music_recommendations(cls, db, emotion_name, user_id=None, limit=4):
        from models import Emotion, MusicRecommendation
        
        emotion = Emotion.query.filter_by(name=emotion_name).first()
        if not emotion:
            return []
        
        music_list = MusicRecommendation.query.filter_by(
            emotion_id=emotion.id
        ).order_by(MusicRecommendation.popularity_score.desc()).limit(limit).all()
        
        return [m.to_dict() for m in music_list]
    
    @classmethod
    def get_emotion_statistics(cls, db, user_id, days=30):
        from models import EmotionHistory
        
        start_date = datetime.now().date() - timedelta(days=days)
        
        history = EmotionHistory.query.filter(
            EmotionHistory.user_id == user_id,
            EmotionHistory.date >= start_date
        ).all()
        
        emotion_counts = Counter()
        daily_emotions = {}
        
        for entry in history:
            emotion_name = entry.emotion.name if entry.emotion else 'Unknown'
            emotion_counts[emotion_name] += 1
            date_str = entry.date.isoformat()
            daily_emotions[date_str] = {
                'emotion': emotion_name,
                'emoji': entry.emotion.emoji if entry.emotion else '😐',
                'color': entry.emotion.color if entry.emotion else '#95A5A6',
                'has_photo': bool(entry.photo_url),
                'notes': entry.notes
            }
        
        total = sum(emotion_counts.values())
        emotion_percentages = {
            emotion: (count / total * 100) if total > 0 else 0
            for emotion, count in emotion_counts.items()
        }
        
        most_common = emotion_counts.most_common(1)
        dominant_emotion = most_common[0][0] if most_common else 'Neutral'
        
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
            pattern.append({
                'date': entry.date.isoformat(),
                'day': entry.date.strftime('%A'),
                'emotion': entry.emotion.name if entry.emotion else 'Unknown',
                'emoji': entry.emotion.emoji if entry.emotion else '😐'
            })
        
        return pattern
    
    @classmethod
    def analyze_mood_factors(cls, sleep_quality, energy_level, stress_level, concentration, motivation, mood_rating):
        """Analyze six factors and determine appropriate emotion"""
        
        norm_sleep = sleep_quality * 2
        norm_energy = energy_level * 2
        norm_stress = (6 - stress_level) * 2
        norm_concentration = concentration * 2
        norm_motivation = motivation * 2
        norm_mood = mood_rating * 2
        
        emotion_scores = {}
        
        emotion_scores['Happy'] = (norm_sleep * 0.15 + norm_energy * 0.2 + norm_stress * 0.15 + norm_concentration * 0.15 + norm_motivation * 0.2 + norm_mood * 0.15) / 10
        emotion_scores['Sad'] = ((10 - norm_mood) * 0.3 + (10 - norm_motivation) * 0.3 + (10 - norm_energy) * 0.2 + (10 - norm_sleep) * 0.2) / 10
        emotion_scores['Tired'] = ((10 - norm_sleep) * 0.4 + (10 - norm_energy) * 0.4 + (10 - norm_motivation) * 0.2) / 10
        emotion_scores['Angry'] = ((10 - norm_stress) * 0.2 + (10 - norm_mood) * 0.2 + (10 - norm_concentration) * 0.3 + norm_energy * 0.3) / 10
        emotion_scores['Stressed'] = ((10 - norm_stress) * 0.1 + (10 - norm_concentration) * 0.3 + norm_sleep * 0.25 + norm_mood * 0.2 + norm_energy * 0.15) / 10
        emotion_scores['Neutral'] = 1 - (abs(norm_energy - 6) + abs(norm_mood - 6) + abs(norm_stress - 6)) / 24
        
        best_emotion = max(emotion_scores, key=emotion_scores.get)
        return best_emotion
