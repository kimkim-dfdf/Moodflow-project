# ==============================================
# MoodFlow - API Routes (학생용 간단 버전)
# ==============================================
# 모든 API 엔드포인트를 정의하는 파일
# Flask 앱에 라우트 등록
# ==============================================

from flask import request, jsonify, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import datetime
import os
import uuid
import time
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError

# Optional Google GenAI import (may be unavailable in some envs)
try:
    from google import genai
    _HAS_GENAI = True
except Exception as e:
    genai = None
    _HAS_GENAI = False

import repository
import recommendation_engine

# GenAI client singleton + executor (initialized if API key present)
logger = logging.getLogger(__name__)
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
_genai_client = None
_executor = ThreadPoolExecutor(max_workers=4)

# Log GenAI initialization status (use print for guaranteed output)
print(f"[GenAI] Module available: {_HAS_GENAI}")
print(f"[GenAI] API Key present: {bool(GOOGLE_API_KEY)}")

if GOOGLE_API_KEY and _HAS_GENAI:
    try:
        _genai_client = genai.Client(api_key=GOOGLE_API_KEY)
        print("✅ [GenAI] Client successfully initialized!")
    except Exception as e:
        print(f"❌ [GenAI] Failed to initialize: {str(e)}")
        _genai_client = None
else:
    if not GOOGLE_API_KEY:
        print("⚠️ [GenAI] API Key not set - GenAI features disabled")
    if not _HAS_GENAI:
        print("⚠️ [GenAI] Module not available - GenAI features disabled")
    if not _HAS_GENAI:
        print("⚠️ [GenAI] Module not available - GenAI features disabled")




def _call_genai(prompt, model='gemini-2.5-flash'):
    """Synchronous call to GenAI client (meant to be run in executor)."""
    if not _genai_client:
        raise RuntimeError("GenAI client not initialized")
    try:
        print(f"[GenAI] Calling model: {model}")
        response = _genai_client.models.generate_content(model=model, contents=prompt)
        print(f"[GenAI] Success! Response received")
        return response
    except Exception as e:
        print(f"[GenAI] Error in _call_genai: {str(e)}")
        raise


# ==============================================
# Configuration (설정)
# ==============================================

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


# ==============================================
# Helper Functions (헬퍼 함수)
# ==============================================

def allowed_file(filename):
    """파일 확장자가 허용되는지 확인"""
    if not filename or '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS


def admin_required(f):
    """관리자 권한 필요 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Login required'}), 401
        if not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


def get_json_or_error():
    """요청에서 JSON 데이터 가져오기 (없으면 에러)"""
    data = request.get_json()
    if not data:
        return None
    return data


# ==============================================
# Route Registration (라우트 등록)
# ==============================================

def register_routes(app):
    """모든 API 라우트를 Flask 앱에 등록"""
    
    # ==========================================
    # Auth Routes (인증)
    # ==========================================
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """로그인"""
        data = get_json_or_error()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        user = repository.get_user_by_email(data['email'])
        if not user or not repository.check_user_password(user, data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        login_user(user)
        return jsonify({'message': 'Login successful', 'user': repository.user_to_dict(user)})
    
    
    @app.route('/api/auth/signup', methods=['POST'])
    def signup():
        """회원가입"""
        data = get_json_or_error()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # 입력값 검증
        if not email or not username or not password:
            return jsonify({'error': 'Email, username, and password required'}), 400
        
        if len(username) < 2:
            return jsonify({'error': 'Username must be at least 2 characters'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # 사용자 생성
        user, error = repository.create_user(email, username, password)
        if error:
            return jsonify({'error': error}), 400
        
        # 자동 로그인
        login_user(user)
        return jsonify({'message': 'Account created successfully', 'user': repository.user_to_dict(user)}), 201
    
    
    @app.route('/api/auth/logout', methods=['POST'])
    @login_required
    def logout():
        """로그아웃"""
        logout_user()
        return jsonify({'message': 'Logged out successfully'})
    
    
    @app.route('/api/auth/me', methods=['GET'])
    @login_required
    def get_current_user_route():
        """현재 로그인한 사용자 정보"""
        return jsonify({'user': current_user.to_dict()})
    
    
    # ==========================================
    # Emotion Routes (감정)
    # ==========================================
    
    @app.route('/api/emotions', methods=['GET'])
    def get_emotions():
        """모든 감정 목록"""
        return jsonify(repository.get_all_emotions())
    
    
    @app.route('/api/emotions/record', methods=['POST'])
    @login_required
    def record_emotion():
        """감정 기록"""
        data = get_json_or_error()
        if not data or not data.get('emotion_id'):
            return jsonify({'error': 'Emotion ID required'}), 400
        
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        entry = repository.create_emotion_entry(
            current_user.id, data['emotion_id'], date,
            data.get('notes'), data.get('photo_url')
        )
        
        entry['emotion'] = repository.get_emotion_by_id(entry['emotion_id'])
        return jsonify({'message': 'Emotion recorded', 'entry': entry})
    
    
    @app.route('/api/emotions/diary/<date_str>', methods=['GET'])
    @login_required
    def get_diary_entry(date_str):
        """특정 날짜의 감정 기록"""
        entry = repository.get_emotion_entry_by_date(current_user.id, date_str)
        if entry:
            entry['emotion'] = repository.get_emotion_by_id(entry['emotion_id'])
            return jsonify(entry)
        return jsonify(None)
    
    
    @app.route('/api/emotions/statistics', methods=['GET'])
    @login_required
    def get_emotion_statistics():
        """감정 통계"""
        days = request.args.get('days', 30, type=int)
        stats = recommendation_engine.get_emotion_statistics_from_repo(current_user.id, days)
        return jsonify(stats)
    
    
    # ==========================================
    # File Upload Routes (파일 업로드)
    # ==========================================
    
    @app.route('/api/upload/photo', methods=['POST'])
    @login_required
    def upload_photo():
        """사진 업로드"""
        if 'photo' not in request.files:
            return jsonify({'error': 'No photo provided'}), 400
        
        file = request.files['photo']
        if not file.filename or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file'}), 400
        
        filename = secure_filename(file.filename)
        unique_filename = uuid.uuid4().hex + '_' + filename
        
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        
        file.save(os.path.join(UPLOAD_FOLDER, unique_filename))
        return jsonify({'photo_url': '/api/uploads/' + unique_filename, 'filename': unique_filename})
    
    
    @app.route('/api/uploads/<filename>')
    def serve_upload(filename):
        """업로드된 파일 제공"""
        return send_from_directory(UPLOAD_FOLDER, filename)
    
    
    # ==========================================
    # Task Routes (할일)
    # ==========================================
    
    @app.route('/api/tasks', methods=['GET'])
    @login_required
    def get_tasks():
        """할일 목록"""
        return jsonify(repository.get_tasks_by_user(current_user.id, request.args.get('date')))
    
    
    @app.route('/api/tasks', methods=['POST'])
    @login_required
    def create_task():
        """할일 생성"""
        data = get_json_or_error()
        if not data or not data.get('title'):
            return jsonify({'error': 'Title required'}), 400
        
        task_date = data.get('task_date', datetime.now().strftime('%Y-%m-%d'))
        
        existing = repository.get_existing_task(current_user.id, data['title'], task_date)
        if existing:
            return jsonify({'error': 'Task already exists', 'task': existing}), 409
        
        task = repository.create_task(
            current_user.id, data['title'],
            data.get('category', 'Personal'), data.get('priority', 'Medium'),
            task_date, data.get('recommended_for_emotion')
        )
        return jsonify(task), 201
    
    
    @app.route('/api/tasks/<int:task_id>', methods=['PUT'])
    @login_required
    def update_task(task_id):
        """할일 수정"""
        task = repository.get_task_by_id(task_id, current_user.id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        data = request.get_json()
        if 'is_completed' in data:
            task = repository.update_task(task_id, current_user.id, data['is_completed'])
        return jsonify(task)
    
    
    @app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
    @login_required
    def delete_task(task_id):
        """할일 삭제"""
        if not repository.delete_task(task_id, current_user.id):
            return jsonify({'error': 'Task not found'}), 404
        return jsonify({'message': 'Task deleted'})
    
    
    @app.route('/api/tasks/recommended', methods=['GET'])
    @login_required
    def get_recommended_tasks():
        """추천 할일"""
        emotion = request.args.get('emotion', 'Neutral')
        limit = request.args.get('limit', 5, type=int)
        recommendations = recommendation_engine.get_recommended_tasks_from_repo(
            current_user.id, emotion, limit, request.args.get('date')
        )
        return jsonify(recommendations)
    
    
    @app.route('/api/tasks/suggestions', methods=['GET'])
    @login_required
    def get_task_suggestions():
        """AI 추천 할일"""
        emotion = request.args.get('emotion', 'Neutral')
        limit = request.args.get('limit', 3, type=int)
        return jsonify(recommendation_engine.get_suggested_tasks(emotion, limit))
    
    
    # ==========================================
    # Music Routes (음악)
    # ==========================================
    
    @app.route('/api/music/recommendations', methods=['GET'])
    def get_music_recommendations():
        """감정에 맞는 음악 추천"""
        emotion = request.args.get('emotion', 'Neutral')
        limit = request.args.get('limit', 4, type=int)
        return jsonify(repository.get_music_by_emotion(emotion, limit))
    
    
    @app.route('/api/music/all', methods=['GET'])
    def get_all_music():
        """모든 음악"""
        return jsonify(repository.get_all_music())
    
    
    @app.route('/api/music/chat', methods=['POST'])
    def music_chat():
        """AI Music Recommendation Chatbot"""
        if not _genai_client:
            return jsonify({'error': 'AI feature is not available'}), 503
        
        data = get_json_or_error()
        if not data or not data.get('message'):
            return jsonify({'error': 'Message required'}), 400
        
        user_message = data.get('message', '').strip()
        
        try:
            prompt = f"""You are a music recommendation assistant. Your ONLY task is to recommend 5 real, popular songs based on the user's emotion.

User's current emotion: "{user_message}"

IMPORTANT RULES:
1. ONLY recommend real songs that actually exist
2. Use real artist names (famous songs from Spotify, YouTube, etc.)
3. Format EXACTLY like this - NO OTHER TEXT:
Song Title - Artist Name
Song Title - Artist Name
Song Title - Artist Name
Song Title - Artist Name
Song Title - Artist Name

Examples of good recommendations:
- If emotion is "sad": "Someone Like You - Adele", "The Night We Met - Lord Huron"
- If emotion is "happy": "Walking on Sunshine - Katrina & The Waves", "Good as Hell - Lizzo"
- If emotion is "energetic": "Blinding Lights - The Weeknd", "Don't Stop Me Now - Queen"
- If emotion is "stressed": "Weightless - Marconi Union", "Calm - Johnny Lang"

NOW RECOMMEND 5 SONGS FOR THIS EMOTION: "{user_message}"
Do not add any explanation. Only list the 5 songs."""
            
            def call_genai():
                return _call_genai(prompt)
            
            response = _executor.submit(call_genai).result(timeout=15)
            reply_text = response.text if hasattr(response, 'text') else str(response)
            
            return jsonify({
                'reply': reply_text,
                'recommendations': []
            })
            
        except TimeoutError:
            return jsonify({'error': 'Response timeout'}), 504
        except Exception as e:
            logger.error(f"Music chat error: {str(e)}")
            return jsonify({'error': 'Chatbot error occurred'}), 500
    
    
    @app.route('/api/music/<int:music_id>', methods=['GET'])
    def get_music_by_id(music_id):
        """음악 상세 정보"""
        music = repository.get_music_by_id(music_id)
        if not music:
            return jsonify({'error': 'Music not found'}), 404
        return jsonify(music)
    
    
    @app.route('/api/music/<int:music_id>/reviews', methods=['GET'])
    def get_music_reviews(music_id):
        """음악 리뷰 목록"""
        return jsonify(repository.get_reviews_for_music(music_id))
    
    
    @app.route('/api/music/<int:music_id>/reviews', methods=['POST'])
    @login_required
    def create_music_review(music_id):
        """음악 리뷰 작성"""
        data = get_json_or_error()
        if not data or not data.get('content'):
            return jsonify({'error': 'Content required'}), 400
        
        review = repository.create_music_review(current_user.id, music_id, data['content'])
        if review is None:
            return jsonify({'error': 'Already reviewed'}), 400
        return jsonify(review), 201
    
    
    @app.route('/api/music/reviews/<int:review_id>', methods=['DELETE'])
    @login_required
    def delete_music_review(review_id):
        """음악 리뷰 삭제"""
        if not repository.delete_music_review(review_id, current_user.id):
            return jsonify({'error': 'Not found'}), 404
        return jsonify({'success': True})
    
    
    @app.route('/api/music/listening-tags', methods=['GET'])
    def get_listening_tags():
        """리스닝 태그 목록"""
        return jsonify(repository.get_all_listening_tags())
    
    
    @app.route('/api/music/<int:music_id>/tags', methods=['GET'])
    def get_music_tags(music_id):
        """음악의 태그"""
        tags = repository.get_music_tags(music_id)
        user_tag_ids = []
        if current_user.is_authenticated:
            user_tag_ids = repository.get_user_music_tags(current_user.id, music_id)
        
        for tag in tags:
            tag['user_tagged'] = tag['id'] in user_tag_ids
        return jsonify(tags)
    
    
    @app.route('/api/music/<int:music_id>/tags/<int:tag_id>', methods=['POST'])
    @login_required
    def add_music_tag(music_id, tag_id):
        """음악에 태그 추가"""
        if not repository.add_user_music_tag(current_user.id, music_id, tag_id):
            return jsonify({'error': 'Tag already added'}), 400
        return jsonify({'success': True}), 201
    
    
    @app.route('/api/music/<int:music_id>/tags/<int:tag_id>', methods=['DELETE'])
    @login_required
    def remove_music_tag(music_id, tag_id):
        """음악에서 태그 제거"""
        if not repository.remove_user_music_tag(current_user.id, music_id, tag_id):
            return jsonify({'error': 'Tag not found'}), 404
        return jsonify({'success': True})
    
    
    # ==========================================
    # Book Routes (책)
    # ==========================================
    
    @app.route('/api/books/tags', methods=['GET'])
    def get_book_tags():
        """책 태그 목록 (책 수 포함)"""
        tags = repository.get_all_book_tags()
        all_books = repository.get_all_books()
        
        result = []
        for tag in tags:
            tag_copy = dict(tag)
            count = 0
            for book in all_books:
                book_tag_slugs = []
                for t in book.get('tags', []):
                    if isinstance(t, dict):
                        book_tag_slugs.append(t.get('slug', ''))
                    else:
                        book_tag_slugs.append(t)
                if tag['slug'] in book_tag_slugs:
                    count = count + 1
            tag_copy['book_count'] = count
            result.append(tag_copy)
        
        # 이름순 정렬 (버블 정렬)
        for i in range(len(result)):
            for j in range(i + 1, len(result)):
                if result[j]['name'] < result[i]['name']:
                    temp = result[i]
                    result[i] = result[j]
                    result[j] = temp
        return jsonify(result)
    
    
    @app.route('/api/books', methods=['GET'])
    def get_books_by_tags():
        """태그로 책 필터링"""
        tag_slugs = request.args.getlist('tags')
        if not tag_slugs:
            tag_slugs = request.args.getlist('tags[]')
        limit = request.args.get('limit', 24, type=int)
        return jsonify(repository.get_books_by_tags(tag_slugs, limit))
    
    
    @app.route('/api/books/popular', methods=['GET'])
    def get_popular_books():
        """인기 책"""
        limit = request.args.get('limit', 5, type=int)
        return jsonify(repository.get_popular_books(limit))
    
    
    @app.route('/api/books/search', methods=['GET'])
    def search_books():
        """책 검색"""
        query = request.args.get('q', '')
        limit = request.args.get('limit', 24, type=int)
        if not query:
            return jsonify([])
        
        query_lower = query.lower()
        all_books = repository.get_all_books()
        result = []
        for book in all_books:
            if query_lower in book['title'].lower() or query_lower in book['author'].lower():
                result.append(book)
        
        if len(result) > limit:
            result = result[:limit]
        return jsonify(result)


    # ==========================================
    # AI Book Emotion Summary (책 감정 요약)
    # ==========================================

    # Simple in-memory TTL cache for AI summaries: {book_id: (timestamp, summary)}
    _ai_summary_cache = {}
    _AI_CACHE_TTL = 60 * 60  # 1 hour

    @app.route('/api/books/<int:book_id>/ai-emotion', methods=['GET'])
    def get_book_ai_emotion(book_id):
        """Return a short emotion-summary for a book using GenAI (cached)."""
        # Try cache
        now = time.time()
        cached = _ai_summary_cache.get(book_id)
        if cached:
            ts, text = cached
            if now - ts < _AI_CACHE_TTL:
                return jsonify({'ai_emotion': text, 'cached': True})
            else:
                _ai_summary_cache.pop(book_id, None)

        # Find book
        all_books = repository.get_all_books()
        book = next((b for b in all_books if b.get('id') == book_id), None)
        if not book:
            return jsonify({'error': 'Book not found'}), 404

        # If GenAI not available, return fallback based on genre/title
        if not _genai_client:
            fallback = f"Readers may feel reflective or moved by {book.get('title')} ({book.get('genre', 'Unknown')})."
            _ai_summary_cache[book_id] = (now, fallback)
            return jsonify({'ai_emotion': fallback, 'cached': False})

        # Compose prompt
        prompt = (
            f"Given the following book metadata, list 2-3 emotions a typical reader might feel when reading it,"
            f" and give a one-sentence reason. Keep it short and friendly.\n\n"
            f"Title: {book.get('title')}\n"
            f"Author: {book.get('author')}\n"
            f"Genre: {book.get('genre')}\n"
            f"Description: {book.get('description', '')}\n"
        )

        future = _executor.submit(_call_genai, prompt)
        try:
            response = future.result(timeout=7.0)  # Increased timeout from 3.0 to 7.0 seconds
            text = getattr(response, 'text', '') or ''
            text = text.strip()
        except TimeoutError:
            future.cancel()
            logger.warning('GenAI timeout for book_id=%s', book_id)
            text = f"Reading {book.get('title')} might evoke curiosity and empathy."
        except Exception:
            logger.exception('GenAI failure for book_id=%s', book_id)
            text = f"Reading {book.get('title')} might evoke curiosity and empathy."

        # Cache and return
        _ai_summary_cache[book_id] = (now, text)
        return jsonify({'ai_emotion': text, 'cached': False})
    
    
    # ==========================================
    # Book Review Routes (책 리뷰)
    # ==========================================
    
    @app.route('/api/books/<int:book_id>/reviews', methods=['GET'])
    def get_book_reviews(book_id):
        """책 리뷰 목록"""
        return jsonify(repository.get_reviews_for_book(book_id))
    
    
    @app.route('/api/books/<int:book_id>/reviews', methods=['POST'])
    @login_required
    def create_review(book_id):
        """책 리뷰 작성"""
        data = request.get_json()
        rating = data.get('rating')
        content = data.get('content', '')
        
        if rating is None or rating < 1 or rating > 5:
            return jsonify({'error': 'Rating 1-5 required'}), 400
        if not content.strip():
            return jsonify({'error': 'Content required'}), 400
        
        review = repository.create_book_review(current_user.id, book_id, rating, content.strip())
        if review is None:
            return jsonify({'error': 'Already reviewed'}), 400
        return jsonify(review), 201
    
    
    @app.route('/api/books/reviews/<int:review_id>', methods=['PUT'])
    @login_required
    def update_review(review_id):
        """책 리뷰 수정"""
        data = request.get_json()
        rating = data.get('rating')
        content = data.get('content', '')
        
        if rating is None or rating < 1 or rating > 5:
            return jsonify({'error': 'Rating 1-5 required'}), 400
        
        review = repository.update_book_review(review_id, current_user.id, rating, content.strip())
        if review is None:
            return jsonify({'error': 'Not found'}), 404
        return jsonify(review)
    
    
    @app.route('/api/books/reviews/<int:review_id>', methods=['DELETE'])
    @login_required
    def delete_review(review_id):
        """책 리뷰 삭제"""
        if not repository.delete_book_review(review_id, current_user.id):
            return jsonify({'error': 'Not found'}), 404
        return jsonify({'message': 'Review deleted'})
    
    
    # ==========================================
    # Profile Routes (프로필)
    # ==========================================
    
    @app.route('/api/user/profile', methods=['PUT'])
    @login_required
    def update_profile():
        """프로필 수정"""
        data = request.get_json()
        if 'username' in data:
            existing = repository.get_user_by_username(data['username'])
            if existing and existing.id != current_user.id:
                return jsonify({'error': 'Username taken'}), 400
            user = repository.update_user(current_user.id, data['username'])
            return jsonify(repository.user_to_dict(user))
        return jsonify(current_user.to_dict())
    
    
    # ==========================================
    # Admin Routes (관리자)
    # ==========================================
    
    @app.route('/api/admin/stats', methods=['GET'])
    @admin_required
    def get_admin_stats():
        """관리자 통계"""
        return jsonify({
            'total_users': len(repository.get_all_users_stats()),
            'users': repository.get_all_users_stats(),
            'emotion_stats': repository.get_overall_emotion_stats(),
            'task_stats': repository.get_overall_task_stats()
        })
    
    
    @app.route('/api/admin/music', methods=['GET'])
    @admin_required
    def get_all_music_admin():
        """관리자 - 모든 음악"""
        return jsonify(repository.get_all_music())
    
    
    @app.route('/api/admin/music', methods=['POST'])
    @admin_required
    def create_music_admin():
        """관리자 - 음악 추가"""
        data = get_json_or_error()
        if not data or not data.get('title'):
            return jsonify({'error': 'Title required'}), 400
        
        result = repository.create_music(
            data.get('emotion', 'Happy'), data['title'],
            data.get('artist', ''), data.get('genre', ''), data.get('youtube_url', '')
        )
        return jsonify(result), 201
    
    
    @app.route('/api/admin/music/<int:music_id>', methods=['PUT'])
    @admin_required
    def update_music_admin(music_id):
        """관리자 - 음악 수정"""
        data = get_json_or_error()
        if not data or not data.get('title'):
            return jsonify({'error': 'Title required'}), 400
        
        result = repository.update_music(
            music_id, data.get('emotion', 'Happy'), data['title'],
            data.get('artist', ''), data.get('genre', ''), data.get('youtube_url', '')
        )
        if result is None:
            return jsonify({'error': 'Not found'}), 404
        return jsonify(result)
    
    
    @app.route('/api/admin/music/<int:music_id>', methods=['DELETE'])
    @admin_required
    def delete_music_admin(music_id):
        """관리자 - 음악 삭제"""
        if not repository.delete_music(music_id):
            return jsonify({'error': 'Not found'}), 404
        return jsonify({'message': 'Deleted'})
    
    
    @app.route('/api/admin/books', methods=['GET'])
    @admin_required
    def get_all_books_admin():
        """관리자 - 모든 책"""
        return jsonify(repository.get_all_books())
    
    
    @app.route('/api/admin/books', methods=['POST'])
    @admin_required
    def create_book_admin():
        """관리자 - 책 추가"""
        data = get_json_or_error()
        if not data or not data.get('title'):
            return jsonify({'error': 'Title required'}), 400
        
        result = repository.create_book(
            data.get('emotion', 'Happy'), data['title'], data.get('author', ''),
            data.get('genre', ''), data.get('description', ''),
            data.get('tags', []), data.get('price', 15.99)
        )
        return jsonify(result), 201
    
    
    @app.route('/api/admin/books/<int:book_id>', methods=['PUT'])
    @admin_required
    def update_book_admin(book_id):
        """관리자 - 책 수정"""
        data = get_json_or_error()
        if not data or not data.get('title'):
            return jsonify({'error': 'Title required'}), 400
        
        result = repository.update_book(
            book_id, data.get('emotion', 'Happy'), data['title'], data.get('author', ''),
            data.get('genre', ''), data.get('description', ''),
            data.get('tags', []), data.get('price', 15.99)
        )
        if result is None:
            return jsonify({'error': 'Not found'}), 404
        return jsonify(result)
    
    
    @app.route('/api/admin/books/<int:book_id>', methods=['DELETE'])
    @admin_required
    def delete_book_admin(book_id):
        """관리자 - 책 삭제"""
        if not repository.delete_book(book_id):
            return jsonify({'error': 'Not found'}), 404
        return jsonify({'message': 'Deleted'})
    
    
    @app.route('/api/admin/tags', methods=['GET'])
    @admin_required
    def get_all_tags_admin():
        """관리자 - 모든 태그"""
        return jsonify(repository.get_all_book_tags())
    
    
    # ==========================================
    # AI Message Routes (AI 메시지)
    # ==========================================
    
    @app.route('/api/ai/comfort-message', methods=['POST'])
    @login_required
    def get_ai_comfort_message():
        """감정에 따른 AI 위로/격려 메시지 생성"""
        data = get_json_or_error()
        if not data or not data.get('emotion'):
            return jsonify({'error': 'Emotion required'}), 400
        
        emotion = data.get('emotion')
        username = current_user.username
        
        fallback_msg = get_fallback_message(emotion)
        
        # Check if GenAI is available
        if not _genai_client:
            print(f"⚠️ [GenAI] Not available (API key: {bool(GOOGLE_API_KEY)}, genai module: {_HAS_GENAI})")
            logger.info(f"GenAI not available (API key: {bool(GOOGLE_API_KEY)}, genai module: {_HAS_GENAI})")
            return jsonify({'message': fallback_msg})

        prompt = f"""You are a caring friend. The user "{username}" is feeling "{emotion}" today.
Write a short, warm comfort or encouragement message in English (2-3 sentences max).
Be genuine and supportive. Don't use emojis. Just plain text."""

        print(f"[GenAI] Starting AI request for emotion: {emotion}")
        start = time.time()
        future = _executor.submit(_call_genai, prompt)
        try:
            response = future.result(timeout=10.0)
            duration = time.time() - start
            print(f"✅ [GenAI] Success! Response time: {duration:.3f}s")
            logger.info("GenAI response time: %.3f s", duration)
            message = getattr(response, 'text', None) or fallback_msg
            print(f"[GenAI] Message: {message[:50]}...")
        except TimeoutError:
            future.cancel()
            print(f"❌ [GenAI] Timeout! (10.0s exceeded)")
            logger.warning("GenAI request timed out for user=%s emotion=%s", username, emotion)
            message = fallback_msg
        except Exception as e:
            print(f"❌ [GenAI] Error: {str(e)}")
            logger.exception("GenAI request failed for user=%s emotion=%s: %s", username, emotion, str(e))
            message = fallback_msg

        if message:
            message = message.strip()
        return jsonify({'message': message})
    
    
    def get_fallback_message(emotion):
        """Fallback message when AI is unavailable"""
        messages = {
            'Happy': "You're feeling great today! Keep that positive energy going.",
            'Sad': "It's okay to feel down sometimes. Tomorrow will be a brighter day.",
            'Tired': "You've been working hard. It's okay to take a break and rest.",
            'Angry': "Take a deep breath. It's okay to feel frustrated sometimes.",
            'Stressed': "You're doing your best, and that's enough. Take things one step at a time.",
            'Neutral': "Thank you for checking in today. You're doing great."
        }
        return messages.get(emotion, "Thank you for checking in today. You're doing great.")
    
    
    @app.route('/api/ai/monthly-analysis', methods=['GET'])
    @login_required
    def get_monthly_analysis():
        """월간 분석: Gemini AI로 일기 데이터 기반 분석 생성"""
        from datetime import datetime
        
        # Get current month's emotion data
        today = datetime.now()
        month_start = today.replace(day=1).strftime('%Y-%m-%d')
        
        # Get all emotions this month
        entries = repository.get_emotion_history_since(current_user.id, month_start)
        
        if not entries:
            return jsonify({
                'summary': "No emotion data recorded this month yet. Start recording your emotions to see insights!",
                'keywords': [],
                'next_month_message': "Looking forward to building more insights about your emotions!"
            })
        
        # Count emotions and extract notes
        emotion_counts = {}
        all_notes = []
        all_emotions = repository.get_all_emotions()
        emotion_map = {e['id']: e for e in all_emotions}
        
        for entry in entries:
            emotion_id = entry.get('emotion_id')
            if emotion_id in emotion_map:
                emotion_name = emotion_map[emotion_id]['name']
                emotion_counts[emotion_name] = emotion_counts.get(emotion_name, 0) + 1
            
            if entry.get('notes'):
                all_notes.append(entry['notes'])
        
        # Extract top keywords (simple word frequency from notes)
        keywords = extract_keywords_from_notes(all_notes)
        
        # Generate summary with Gemini AI
        total_entries = len(entries)
        most_common_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else 'Neutral'
        
        # Prepare data for AI prompt
        emotion_stats = ''
        for emotion_name in emotion_counts:
            count = emotion_counts[emotion_name]
            emotion_stats = emotion_stats + emotion_name + ' (' + str(count) + ' times), '
        emotion_stats = emotion_stats.rstrip(', ')
        
        notes_summary = ' | '.join(all_notes[:10])
        if len(all_notes) > 10:
            notes_summary = notes_summary + '...'
        
        # Call Gemini AI for analysis
        summary = generate_ai_monthly_summary(current_user.username, total_entries, most_common_emotion, emotion_stats, notes_summary, keywords)
        
        # Generate next month message with AI
        next_month_message = generate_ai_next_month_message(most_common_emotion, current_user.username)
        
        return jsonify({
            'summary': summary,
            'keywords': keywords,
            'next_month_message': next_month_message
        })
    
    
    def extract_keywords_from_notes(notes_list):
        """일기 노트에서 주요 키워드 추출"""
        if not notes_list:
            return []
        
        # Common words to skip
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'is', 'are', 'was', 'were', 'i', 'me', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'that', 'this', 'these', 'those', 'be', 'have', 'do', 'with', 'from', 'as', 'by', 'about', 'so', 'not', 'just', 'can', 'will', 'had', 'been', 'being', 'did', 'does', 'having', 'may', 'should', 'would', 'could', 'might', 'must'}
        
        word_freq = {}
        all_text = ' '.join(notes_list).lower()
        
        # Simple word extraction (split by spaces and punctuation)
        import re
        words = re.findall(r'\b[a-z]+\b', all_text)
        
        for word in words:
            if len(word) > 3 and word not in stopwords:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top 5
        sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        return [kw[0] for kw in sorted_keywords]
    
    
    def generate_ai_monthly_summary(username, total_entries, most_common_emotion, emotion_stats, notes_summary, keywords):
        """Gemini AI로 월간 요약 생성"""
        fallback_summary = f"This month, you recorded {total_entries} emotion entries. Your most frequent emotion was {most_common_emotion}. Keep tracking your emotional journey!"
        
        if not _genai_client:
            print(f"⚠️ [GenAI] Not available for monthly analysis")
            return fallback_summary
        
        prompt = f"""Analyze this month's emotional journey for {username}:
- Total entries: {total_entries}
- Most common emotion: {most_common_emotion}
- Emotion distribution: {emotion_stats}
- Notable entries: {notes_summary}

Write a warm, personalized 3-4 sentence summary about their emotional journey this month. 
Be empathetic, encouraging, and specific to their data.
Focus on patterns, growth, and positive aspects.
Write in plain English, no emojis."""
        
        print(f"[GenAI] Calling AI for monthly summary analysis")
        start = time.time()
        future = _executor.submit(_call_genai, prompt, 'gemini-2.5-flash')
        try:
            response = future.result(timeout=15.0)
            duration = time.time() - start
            print(f"✅ [GenAI] Monthly analysis success! ({duration:.3f}s)")
            summary = getattr(response, 'text', None) or fallback_summary
        except TimeoutError:
            future.cancel()
            print(f"❌ [GenAI] Monthly analysis timeout")
            summary = fallback_summary
        except Exception as e:
            print(f"❌ [GenAI] Monthly analysis error: {str(e)}")
            summary = fallback_summary
        
        if summary:
            summary = summary.strip()
        return summary
    
    
    def generate_ai_next_month_message(emotion, username):
        """Gemini AI로 다음 달 격려 메시지 생성"""
        fallback_msg = f"Keep tracking your emotions next month, {username}! Your awareness is the first step to growth."
        
        if not _genai_client:
            return fallback_msg
        
        prompt = f"""Write a short, personalized, and encouraging message for {username} for next month.
They were feeling mostly {emotion} this month.
Make it warm, hopeful, and 1-2 sentences max.
No emojis, just genuine encouragement about their emotional journey and growth."""
        
        print(f"[GenAI] Calling AI for next month message")
        start = time.time()
        future = _executor.submit(_call_genai, prompt, 'gemini-2.5-flash')
        try:
            response = future.result(timeout=10.0)
            duration = time.time() - start
            print(f"✅ [GenAI] Next month message success! ({duration:.3f}s)")
            message = getattr(response, 'text', None) or fallback_msg
        except TimeoutError:
            future.cancel()
            print(f"❌ [GenAI] Next month message timeout")
            message = fallback_msg
        except Exception as e:
            print(f"❌ [GenAI] Next month message error: {str(e)}")
            message = fallback_msg
        
        if message:
            message = message.strip()
        return message
    
    
    def generate_monthly_summary(most_common_emotion, total_entries, emotion_counts, username):
        """[DEPRECATED] Use generate_ai_monthly_summary instead"""
        if total_entries == 0:
            return f"Hello {username}! You haven't recorded any emotions this month yet."
        
        emotion_desc = {
            'Happy': 'enjoying positive moments',
            'Sad': 'navigating some challenging feelings',
            'Tired': 'managing your energy and rest',
            'Angry': 'processing strong emotions',
            'Stressed': 'working through stressful times',
            'Neutral': 'staying balanced'
        }
        
        description = emotion_desc.get(most_common_emotion, 'recording your emotional journey')
        summary = f"This month, you recorded {total_entries} emotion entries, with {most_common_emotion} being your most frequent mood. You've been {description}. "
        
        # Add encouragement based on emotion balance
        emotion_variety = len(emotion_counts)
        if emotion_variety >= 5:
            summary += "Your diverse emotional range shows growth and self-awareness!"
        elif emotion_variety >= 3:
            summary += "You're experiencing a healthy mix of emotions."
        else:
            summary += "Keep exploring and expressing your feelings."
        
        return summary
    
    
    # ==========================================
    # Dashboard Routes (대시보드)
    # ==========================================
    
    @app.route('/api/dashboard/summary', methods=['GET'])
    @login_required
    def get_dashboard_summary():
        """대시보드 요약"""
        today = datetime.now().strftime('%Y-%m-%d')
        today_emotion = repository.get_emotion_entry_by_date(current_user.id, today)
        task_counts = repository.count_tasks(current_user.id)
        today_tasks = repository.get_today_due_tasks(current_user.id, today)
        emotion_stats = recommendation_engine.get_emotion_statistics_from_repo(current_user.id, 7)
        
        today_emotion_dict = None
        if today_emotion:
            today_emotion_dict = dict(today_emotion)
            today_emotion_dict['emotion'] = repository.get_emotion_by_id(today_emotion['emotion_id'])
        
        return jsonify({
            'user': repository.user_to_dict(current_user),
            'today_emotion': today_emotion_dict,
            'task_summary': {
                'total': task_counts['total'],
                'completed': task_counts['completed'],
                'pending': task_counts['total'] - task_counts['completed'],
                'today_count': len(today_tasks)
            },
            'emotion_stats': emotion_stats
        })
    
    
