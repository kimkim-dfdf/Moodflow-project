# -*- coding: utf-8 -*-
"""
MoodFlow 추천 엔진
- 감정 기반으로 할일과 음악을 추천해주는 핵심 알고리즘
- 작성일: 2024년
"""

from datetime import datetime, timedelta
from collections import Counter
import random


class EmotionRecommendationEngine:
    """
    감정 기반 추천 시스템
    
    사용자의 현재 감정에 따라:
    1. 어떤 종류의 할일을 먼저 하면 좋을지 추천
    2. 기분에 맞는 음악 추천
    3. 새로운 할일 제안
    """
    
    # ============================================
    # 감정별 할일 카테고리 가중치
    # - 각 감정일 때 어떤 카테고리의 일을 하면 좋을지 점수로 표현
    # - 점수가 높을수록 해당 감정일 때 추천됨
    # ============================================
    EMOTION_TASK_WEIGHTS = {
        # 기분 좋을 때 -> 업무나 공부에 집중하기 좋음
        'Happy': {
            'Work': 1.0,      # 업무 최우선
            'Study': 0.9,     # 공부도 좋음
            'Health': 0.8,
            'Personal': 0.7,
            'priority_preference': 'High',  # 어려운 일 도전하기 좋음
            'energy_tasks': True
        },
        
        # 슬플 때 -> 개인 시간이나 가벼운 일 추천
        'Sad': {
            'Personal': 1.0,  # 나를 위한 시간
            'Health': 0.8,    # 산책 같은 것
            'Study': 0.5,
            'Work': 0.4,      # 업무는 나중에
            'priority_preference': 'Low',
            'energy_tasks': False
        },
        
        # 피곤할 때 -> 쉬운 일 위주로
        'Tired': {
            'Personal': 1.0,
            'Health': 0.7,    # 가벼운 스트레칭
            'Study': 0.4,
            'Work': 0.3,      # 복잡한 업무는 피하기
            'priority_preference': 'Low',
            'energy_tasks': False
        },
        
        # 화날 때 -> 운동으로 에너지 발산
        'Angry': {
            'Health': 1.0,    # 운동 강력 추천
            'Personal': 0.7,
            'Work': 0.5,      # 에너지를 업무에 쏟기
            'Study': 0.4,
            'priority_preference': 'Medium',
            'energy_tasks': True  # 활동적인 일
        },
        
        # 스트레스 받을 때 -> 건강 관리 우선
        'Stressed': {
            'Health': 1.0,    # 명상, 산책 등
            'Personal': 0.8,
            'Work': 0.6,      # 작은 업무부터
            'Study': 0.5,
            'priority_preference': 'Medium',
            'energy_tasks': False
        },
        
        # 평범할 때 -> 골고루
        'Neutral': {
            'Work': 0.8,
            'Study': 0.8,
            'Health': 0.7,
            'Personal': 0.7,
            'priority_preference': 'Medium',
            'energy_tasks': True
        }
    }
    
    # 우선순위별 기본 점수
    PRIORITY_SCORES = {
        'High': 3,    # 중요한 일
        'Medium': 2,  # 보통
        'Low': 1      # 여유로운 일
    }
    
    # ============================================
    # 감정별 추천 할일 목록
    # - 사용자가 할일이 없을 때 제안해주는 템플릿
    # ============================================
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
        """
        할일의 추천 점수 계산 (0~100점)
        
        점수 구성:
        - 카테고리 점수 (40점): 현재 감정에 맞는 카테고리인지
        - 우선순위 점수 (20점): 감정에 맞는 우선순위인지  
        - 긴급도 점수 (30점): 마감일이 가까운지
        - 개인 선호 점수 (10점): 사용자가 선호하는 카테고리인지
        """
        # 해당 감정의 가중치 가져오기
        weights = cls.EMOTION_TASK_WEIGHTS.get(emotion_name, cls.EMOTION_TASK_WEIGHTS['Neutral'])
        
        # 1. 카테고리 점수 (최대 40점)
        category_weight = weights.get(task.category, 0.5)
        category_score = category_weight * 40
        
        # 2. 우선순위 점수 (최대 20점)
        preferred_priority = weights.get('priority_preference', 'Medium')
        priority_match = 1.0 if task.priority == preferred_priority else 0.7
        base_priority = cls.PRIORITY_SCORES.get(task.priority, 2)
        priority_score = base_priority * priority_match * 20
        
        # 3. 긴급도 점수 (최대 30점) - 마감일 기준
        urgency_score = 0
        if task.due_date:
            days_left = (task.due_date - datetime.now().date()).days
            
            if days_left <= 0:      # 오늘 마감이거나 지남
                urgency_score = 30
            elif days_left <= 1:    # 내일까지
                urgency_score = 25
            elif days_left <= 3:    # 3일 이내
                urgency_score = 15
            elif days_left <= 7:    # 일주일 이내
                urgency_score = 5
        
        # 4. 개인 선호도 점수 (최대 10점)
        personal_score = 0
        if user and user.preferred_categories:
            user_favorites = user.preferred_categories.split(',')
            if task.category in user_favorites:
                # 순위에 따라 점수 차등 부여
                rank = user_favorites.index(task.category)
                personal_score = 10 * (1 - rank * 0.1)
        
        # 최종 점수 계산
        total = category_score + priority_score + urgency_score + personal_score
        
        # 0~100 범위로 제한
        return min(100, max(0, total))
    
    @classmethod
    def get_recommended_tasks(cls, db, user_id, emotion_name, limit=5, task_date=None):
        """
        사용자의 할일 목록에서 현재 감정에 맞는 할일 추천
        
        Args:
            user_id: 사용자 ID
            emotion_name: 현재 감정 (예: 'Happy', 'Sad')
            limit: 최대 추천 개수
            task_date: 특정 날짜의 할일만 조회 (선택)
            
        Returns:
            점수순으로 정렬된 추천 할일 목록
        """
        from models import Task, User
        
        # 미완료 할일만 조회
        query = Task.query.filter_by(
            user_id=user_id,
            is_completed=False
        )
        
        # 특정 날짜 필터
        if task_date:
            query = query.filter_by(task_date=task_date)
        
        all_tasks = query.all()
        current_user = User.query.get(user_id)
        
        # 각 할일의 점수 계산
        scored_list = []
        for task in all_tasks:
            score = cls.calculate_task_score(task, emotion_name, current_user)
            scored_list.append((task, score))
        
        # 점수 높은 순으로 정렬
        scored_list.sort(key=lambda x: x[1], reverse=True)
        
        # 상위 N개만 반환
        result = []
        for task, score in scored_list[:limit]:
            result.append({
                'task': task.to_dict(),
                'score': score
            })
        
        return result
    
    @classmethod
    def get_suggested_tasks(cls, emotion_name, limit=3):
        """
        새로운 할일 제안 (할일이 없을 때 보여줌)
        
        Args:
            emotion_name: 현재 감정
            limit: 제안 개수
            
        Returns:
            감정에 맞는 할일 제안 목록
        """
        suggestions = cls.EMOTION_TASK_SUGGESTIONS.get(
            emotion_name, 
            cls.EMOTION_TASK_SUGGESTIONS['Neutral']
        )
        
        # 랜덤으로 섞어서 반환
        selected = random.sample(suggestions, min(limit, len(suggestions)))
        return selected
    
    @classmethod
    def get_music_recommendations(cls, db, emotion_name, user_id=None, limit=4):
        """
        감정에 맞는 음악 추천
        
        Args:
            emotion_name: 현재 감정
            limit: 추천 개수
            
        Returns:
            인기순으로 정렬된 음악 목록
        """
        from models import Emotion, MusicRecommendation
        
        # 감정 찾기
        emotion = Emotion.query.filter_by(name=emotion_name).first()
        if not emotion:
            return []
        
        # 해당 감정의 음악 목록 (인기순)
        music_list = MusicRecommendation.query.filter_by(
            emotion_id=emotion.id
        ).order_by(
            MusicRecommendation.popularity_score.desc()
        ).limit(limit).all()
        
        return [m.to_dict() for m in music_list]
    
    @classmethod
    def get_emotion_statistics(cls, db, user_id, days=30):
        """
        감정 통계 데이터 조회
        
        Args:
            user_id: 사용자 ID
            days: 최근 며칠간의 데이터를 볼 것인지
            
        Returns:
            감정별 횟수, 비율, 일별 기록 등
        """
        from models import EmotionHistory
        
        # 조회 기간 설정
        start_date = datetime.now().date() - timedelta(days=days)
        
        # 해당 기간의 감정 기록 조회
        history = EmotionHistory.query.filter(
            EmotionHistory.user_id == user_id,
            EmotionHistory.date >= start_date
        ).all()
        
        # 감정별 횟수 집계
        emotion_counts = Counter()
        daily_emotions = {}
        
        for entry in history:
            emotion_name = entry.emotion.name if entry.emotion else 'Unknown'
            emotion_counts[emotion_name] += 1
            
            # 날짜별 감정 기록
            date_str = entry.date.isoformat()
            daily_emotions[date_str] = {
                'emotion': emotion_name,
                'emoji': entry.emotion.emoji if entry.emotion else '😐',
                'color': entry.emotion.color if entry.emotion else '#95A5A6',
                'has_photo': bool(entry.photo_url),
                'notes': entry.notes
            }
        
        # 비율 계산
        total = sum(emotion_counts.values())
        percentages = {}
        for emotion, count in emotion_counts.items():
            if total > 0:
                percentages[emotion] = (count / total) * 100
            else:
                percentages[emotion] = 0
        
        # 가장 많이 느낀 감정 찾기
        most_common = emotion_counts.most_common(1)
        dominant = most_common[0][0] if most_common else 'Neutral'
        
        return {
            'counts': dict(emotion_counts),
            'percentages': percentages,
            'dominant_emotion': dominant,
            'total_entries': total,
            'daily_emotions': daily_emotions,
            'period_days': days
        }
    
    @classmethod
    def get_weekly_pattern(cls, db, user_id):
        """
        최근 일주일 감정 패턴 조회
        
        Returns:
            요일별 감정 기록 목록
        """
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
                'day': entry.date.strftime('%A'),  # 요일 이름
                'emotion': entry.emotion.name if entry.emotion else 'Unknown',
                'emoji': entry.emotion.emoji if entry.emotion else '😐'
            })
        
        return pattern
