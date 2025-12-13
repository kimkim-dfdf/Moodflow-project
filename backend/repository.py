# ==============================================
# MoodFlow - Data Repository (학생용 간단 버전)
# ==============================================
# 데이터베이스 작업을 처리하는 파일
# PostgreSQL + SQLAlchemy ORM 사용
# ==============================================

from datetime import datetime
from models import db, User, Task, EmotionHistory, Emotion, Music, BookTag, Book, BookReview


# ==============================================
# Helper Function (헬퍼 함수)
# ==============================================

def to_dict_list(records):
    """
    여러 개의 데이터베이스 레코드를 딕셔너리 리스트로 변환
    Convert multiple database records to a list of dictionaries.
    """
    result = []
    for record in records:
        result.append(record.to_dict())
    return result


# ==============================================
# User Operations (사용자 관련)
# ==============================================

def get_user_by_email(email):
    """이메일로 사용자 찾기"""
    return User.query.filter_by(email=email).first()


def check_user_password(user, password):
    """비밀번호 확인 (데모용 - 단순 비교)"""
    if user.password == password:
        return True
    return False


def user_to_dict(user):
    """사용자 객체를 딕셔너리로 변환"""
    return user.to_dict()


def get_user_by_username(username):
    """사용자명으로 사용자 찾기"""
    return User.query.filter_by(username=username).first()


def update_user(user_id, new_username):
    """사용자명 업데이트"""
    user = db.session.get(User, int(user_id))
    if user:
        user.username = new_username
        db.session.commit()
        return user
    return None


# ==============================================
# Task Operations (할일 관련)
# ==============================================

def create_task(user_id, title, category, priority, task_date, recommended_for_emotion):
    """새 할일 생성"""
    task = Task()
    task.user_id = user_id
    task.title = title
    task.category = category
    task.priority = priority
    task.is_completed = False
    task.task_date = task_date
    task.created_at = datetime.utcnow()
    task.recommended_for_emotion = recommended_for_emotion
    
    db.session.add(task)
    db.session.commit()
    return task.to_dict()


def get_tasks_by_user(user_id, task_date):
    """사용자의 할일 목록 가져오기"""
    query = Task.query.filter_by(user_id=user_id)
    if task_date:
        query = query.filter_by(task_date=task_date)
    query = query.order_by(Task.created_at.desc())
    return to_dict_list(query.all())


def get_incomplete_tasks_by_user(user_id, task_date):
    """미완료 할일 목록 가져오기"""
    query = Task.query.filter_by(user_id=user_id, is_completed=False)
    if task_date:
        query = query.filter_by(task_date=task_date)
    return to_dict_list(query.all())


def get_task_by_id(task_id, user_id):
    """특정 할일 가져오기"""
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if task:
        return task.to_dict()
    return None


def get_existing_task(user_id, title, task_date):
    """중복 할일 확인"""
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
    """할일 완료 상태 업데이트"""
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
    """할일 삭제"""
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if task:
        db.session.delete(task)
        db.session.commit()
        return True
    return False


def count_tasks(user_id):
    """할일 개수 세기"""
    total = Task.query.filter_by(user_id=user_id).count()
    completed = Task.query.filter_by(user_id=user_id, is_completed=True).count()
    return {'total': total, 'completed': completed}


def get_today_due_tasks(user_id, today):
    """오늘 해야 할 할일 가져오기"""
    tasks = Task.query.filter_by(user_id=user_id, task_date=today, is_completed=False).all()
    return to_dict_list(tasks)


# ==============================================
# Emotion Operations (감정 관련)
# ==============================================

def get_all_emotions():
    """모든 감정 가져오기"""
    return to_dict_list(Emotion.query.all())


def get_emotion_by_id(emotion_id):
    """ID로 감정 가져오기"""
    emotion = db.session.get(Emotion, int(emotion_id))
    if emotion:
        return emotion.to_dict()
    return None


def create_emotion_entry(user_id, emotion_id, date, notes, photo_url):
    """감정 기록 생성 또는 업데이트"""
    existing = EmotionHistory.query.filter_by(user_id=user_id, date=date).first()
    
    if existing:
        existing.emotion_id = emotion_id
        existing.recorded_at = datetime.utcnow()
        if notes:
            existing.notes = notes
        if photo_url:
            existing.photo_url = photo_url
        db.session.commit()
        return existing.to_dict()
    
    entry = EmotionHistory()
    entry.user_id = user_id
    entry.emotion_id = emotion_id
    entry.date = date
    entry.notes = notes
    entry.photo_url = photo_url
    entry.recorded_at = datetime.utcnow()
    
    db.session.add(entry)
    db.session.commit()
    return entry.to_dict()


def get_emotion_entry_by_date(user_id, date):
    """특정 날짜의 감정 기록 가져오기"""
    entry = EmotionHistory.query.filter_by(user_id=user_id, date=date).first()
    if entry:
        return entry.to_dict()
    return None


def get_emotion_history_since(user_id, start_date):
    """특정 날짜 이후의 감정 기록 가져오기"""
    entries = EmotionHistory.query.filter(
        EmotionHistory.user_id == user_id,
        EmotionHistory.date >= start_date
    ).all()
    return to_dict_list(entries)


# ==============================================
# Music Operations (음악 관련)
# ==============================================

def get_all_music():
    """모든 음악 가져오기"""
    return to_dict_list(Music.query.all())


def get_music_by_id(music_id):
    """ID로 음악 가져오기"""
    music = db.session.get(Music, int(music_id))
    if music:
        return music.to_dict()
    return None


def get_music_by_emotion(emotion_name, limit):
    """감정에 맞는 음악 가져오기"""
    music_list = Music.query.filter_by(emotion=emotion_name).all()
    result = to_dict_list(music_list)
    if limit and limit < len(result):
        return result[:limit]
    return result


def create_music(emotion, title, artist, genre, youtube_url):
    """새 음악 생성"""
    new_music = Music(emotion=emotion, title=title, artist=artist, genre=genre, youtube_url=youtube_url)
    db.session.add(new_music)
    db.session.commit()
    return new_music.to_dict()


def update_music(music_id, emotion, title, artist, genre, youtube_url):
    """음악 정보 업데이트"""
    music = Music.query.filter_by(id=music_id).first()
    if music is None:
        return None
    music.emotion = emotion
    music.title = title
    music.artist = artist
    music.genre = genre
    music.youtube_url = youtube_url
    db.session.commit()
    return music.to_dict()


def delete_music(music_id):
    """음악 삭제"""
    music = Music.query.filter_by(id=music_id).first()
    if music is None:
        return False
    db.session.delete(music)
    db.session.commit()
    return True


# ==============================================
# Book Operations (책 관련)
# ==============================================

def get_all_tags_as_dict():
    """모든 태그를 딕셔너리로 가져오기 (slug: tag)"""
    all_tags = BookTag.query.all()
    result = {}
    for tag in all_tags:
        result[tag.slug] = tag.to_dict()
    return result


def get_tag_objects_for_book(book_dict, tags_cache=None):
    """책의 태그 슬러그를 태그 객체로 변환"""
    if tags_cache is None:
        tags_cache = get_all_tags_as_dict()
    
    result = []
    tag_slugs = book_dict.get('tags', [])
    if isinstance(tag_slugs, str):
        tag_slugs = tag_slugs.split(',')
    
    for tag_slug in tag_slugs:
        if tag_slug in tags_cache:
            result.append(tags_cache[tag_slug])
    return result


def get_all_book_tags():
    """모든 책 태그 가져오기"""
    return to_dict_list(BookTag.query.all())


def get_all_books():
    """모든 책 가져오기 (태그 포함)"""
    books = Book.query.all()
    tags_cache = get_all_tags_as_dict()
    result = []
    for book in books:
        book_dict = book.to_dict()
        book_dict['tags'] = get_tag_objects_for_book(book_dict, tags_cache)
        result.append(book_dict)
    return result


def get_books_by_tags(tag_slugs, limit):
    """태그로 책 필터링 (AND 로직)"""
    books = Book.query.all()
    tags_cache = get_all_tags_as_dict()
    result = []
    
    for book in books:
        book_tags = book.tags.split(',') if book.tags else []
        
        # 태그 필터가 없으면 모든 책 포함
        if not tag_slugs:
            book_dict = book.to_dict()
            book_dict['tags'] = get_tag_objects_for_book(book_dict, tags_cache)
            result.append(book_dict)
        else:
            # 모든 태그가 일치하는지 확인
            match_count = 0
            for tag in tag_slugs:
                if tag in book_tags:
                    match_count = match_count + 1
            
            if match_count == len(tag_slugs):
                book_dict = book.to_dict()
                book_dict['tags'] = get_tag_objects_for_book(book_dict, tags_cache)
                result.append(book_dict)
    
    if limit and limit < len(result):
        return result[:limit]
    return result


def create_book(emotion, title, author, genre, description, tags, price=15.99):
    """새 책 생성"""
    tags_str = ','.join(tags) if tags else ''
    new_book = Book(emotion=emotion, title=title, author=author, genre=genre, 
                    description=description, tags=tags_str, price=price)
    db.session.add(new_book)
    db.session.commit()
    result = new_book.to_dict()
    result['tags'] = get_tag_objects_for_book(result)
    return result


def update_book(book_id, emotion, title, author, genre, description, tags, price=15.99):
    """책 정보 업데이트"""
    book = Book.query.filter_by(id=book_id).first()
    if book is None:
        return None
    
    book.emotion = emotion
    book.title = title
    book.author = author
    book.genre = genre
    book.description = description
    book.tags = ','.join(tags) if tags else ''
    book.price = price
    db.session.commit()
    
    result = book.to_dict()
    result['tags'] = get_tag_objects_for_book(result)
    return result


def delete_book(book_id):
    """책 삭제"""
    book = Book.query.filter_by(id=book_id).first()
    if book is None:
        return False
    db.session.delete(book)
    db.session.commit()
    return True


# ==============================================
# Book Review Operations (책 리뷰 관련)
# ==============================================

def get_reviews_for_book(book_id):
    """책의 모든 리뷰 가져오기"""
    reviews = BookReview.query.filter_by(book_id=book_id).order_by(BookReview.created_at.desc()).all()
    result = []
    for review in reviews:
        review_dict = review.to_dict()
        user = db.session.get(User, review.user_id)
        review_dict['username'] = user.username if user else 'Unknown'
        result.append(review_dict)
    return result


def create_book_review(user_id, book_id, rating, content):
    """책 리뷰 생성 (사용자당 1개만)"""
    existing = BookReview.query.filter_by(user_id=user_id, book_id=book_id).first()
    if existing:
        return None
    
    review = BookReview()
    review.user_id = user_id
    review.book_id = book_id
    review.rating = rating
    review.content = content
    review.created_at = datetime.utcnow()
    
    db.session.add(review)
    db.session.commit()
    
    result = review.to_dict()
    user = db.session.get(User, user_id)
    if user:
        result['username'] = user.username
    return result


def update_book_review(review_id, user_id, rating, content):
    """책 리뷰 수정"""
    review = BookReview.query.filter_by(id=review_id, user_id=user_id).first()
    if review is None:
        return None
    
    review.rating = rating
    review.content = content
    db.session.commit()
    
    result = review.to_dict()
    user = db.session.get(User, user_id)
    if user:
        result['username'] = user.username
    return result


def delete_book_review(review_id, user_id):
    """책 리뷰 삭제"""
    review = BookReview.query.filter_by(id=review_id, user_id=user_id).first()
    if review is None:
        return False
    db.session.delete(review)
    db.session.commit()
    return True


def get_popular_books(limit=10):
    """리뷰 수가 많은 인기 책 가져오기"""
    books = Book.query.all()
    tags_cache = get_all_tags_as_dict()
    
    books_with_counts = []
    for book in books:
        review_count = BookReview.query.filter_by(book_id=book.id).count()
        book_dict = book.to_dict()
        book_dict['tags'] = get_tag_objects_for_book(book_dict, tags_cache)
        book_dict['review_count'] = review_count
        books_with_counts.append(book_dict)
    
    # 버블 정렬 (리뷰 수 내림차순)
    for i in range(len(books_with_counts)):
        for j in range(i + 1, len(books_with_counts)):
            if books_with_counts[j]['review_count'] > books_with_counts[i]['review_count']:
                temp = books_with_counts[i]
                books_with_counts[i] = books_with_counts[j]
                books_with_counts[j] = temp
    
    if limit and limit < len(books_with_counts):
        return books_with_counts[:limit]
    return books_with_counts


# ==============================================
# Music Review Operations (음악 리뷰 관련)
# ==============================================

def get_reviews_for_music(music_id):
    """음악의 모든 리뷰 가져오기"""
    from models import MusicReview, UserMusicTag, MusicListeningTag
    reviews = MusicReview.query.filter_by(music_id=music_id).order_by(MusicReview.created_at.desc()).all()
    
    result = []
    for review in reviews:
        review_dict = review.to_dict()
        user = db.session.get(User, review.user_id)
        review_dict['username'] = user.username if user else 'Unknown'
        
        # 사용자의 리스닝 태그 가져오기
        user_tags = UserMusicTag.query.filter_by(user_id=review.user_id, music_id=music_id).all()
        tag_names = []
        for user_tag in user_tags:
            tag = db.session.get(MusicListeningTag, user_tag.tag_id)
            if tag:
                tag_names.append(tag.name)
        review_dict['listening_tags'] = tag_names
        result.append(review_dict)
    return result


def create_music_review(user_id, music_id, content):
    """음악 리뷰 생성 (사용자당 1개만)"""
    from models import MusicReview
    existing = MusicReview.query.filter_by(user_id=user_id, music_id=music_id).first()
    if existing:
        return None
    
    review = MusicReview()
    review.user_id = user_id
    review.music_id = music_id
    review.content = content
    review.created_at = datetime.utcnow()
    
    db.session.add(review)
    db.session.commit()
    
    result = review.to_dict()
    user = db.session.get(User, user_id)
    if user:
        result['username'] = user.username
    return result


def delete_music_review(review_id, user_id):
    """음악 리뷰 삭제"""
    from models import MusicReview
    review = MusicReview.query.filter_by(id=review_id, user_id=user_id).first()
    if review is None:
        return False
    db.session.delete(review)
    db.session.commit()
    return True


# ==============================================
# Music Listening Tags (음악 리스닝 태그)
# ==============================================

def get_all_listening_tags():
    """모든 리스닝 태그 가져오기"""
    from models import MusicListeningTag
    return to_dict_list(MusicListeningTag.query.all())


def get_music_tags(music_id):
    """음악에 달린 태그와 개수 가져오기"""
    from models import UserMusicTag, MusicListeningTag
    all_tags = MusicListeningTag.query.all()
    
    result = []
    for tag in all_tags:
        count = UserMusicTag.query.filter_by(music_id=music_id, tag_id=tag.id).count()
        tag_dict = tag.to_dict()
        tag_dict['count'] = count
        result.append(tag_dict)
    return result


def get_user_music_tags(user_id, music_id):
    """사용자가 해당 음악에 단 태그 ID 목록"""
    from models import UserMusicTag
    user_tags = UserMusicTag.query.filter_by(user_id=user_id, music_id=music_id).all()
    result = []
    for ut in user_tags:
        result.append(ut.tag_id)
    return result


def add_user_music_tag(user_id, music_id, tag_id):
    """음악에 태그 추가"""
    from models import UserMusicTag
    existing = UserMusicTag.query.filter_by(user_id=user_id, music_id=music_id, tag_id=tag_id).first()
    if existing:
        return False
    
    user_tag = UserMusicTag()
    user_tag.user_id = user_id
    user_tag.music_id = music_id
    user_tag.tag_id = tag_id
    db.session.add(user_tag)
    db.session.commit()
    return True


def remove_user_music_tag(user_id, music_id, tag_id):
    """음악에서 태그 제거"""
    from models import UserMusicTag
    user_tag = UserMusicTag.query.filter_by(user_id=user_id, music_id=music_id, tag_id=tag_id).first()
    if user_tag is None:
        return False
    db.session.delete(user_tag)
    db.session.commit()
    return True


# ==============================================
# Admin Statistics (관리자 통계)
# ==============================================

def get_all_users_stats():
    """모든 사용자 통계"""
    users = User.query.filter_by(is_admin=False).all()
    
    stats = []
    for user in users:
        task_counts = count_tasks(user.id)
        emotion_count = EmotionHistory.query.filter_by(user_id=user.id).count()
        stats.append({
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'total_tasks': task_counts['total'],
            'completed_tasks': task_counts['completed'],
            'emotion_entries': emotion_count
        })
    return stats


def get_overall_emotion_stats():
    """전체 감정 통계"""
    entries = EmotionHistory.query.all()
    emotion_counts = {}
    for entry in entries:
        emotion_id = entry.emotion_id
        if emotion_id in emotion_counts:
            emotion_counts[emotion_id] = emotion_counts[emotion_id] + 1
        else:
            emotion_counts[emotion_id] = 1
    return emotion_counts


def get_overall_task_stats():
    """전체 할일 통계"""
    total = Task.query.count()
    completed = Task.query.filter_by(is_completed=True).count()
    
    tasks = Task.query.all()
    category_counts = {}
    for task in tasks:
        category = task.category
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


