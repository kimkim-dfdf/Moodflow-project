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

import repository
import recommendation_engine


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
    
    
    @app.route('/api/admin/orders', methods=['GET'])
    @admin_required
    def get_all_orders_admin():
        """관리자 - 모든 주문"""
        return jsonify(repository.get_all_orders_admin())
    
    
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
    
    
    # ==========================================
    # Cart Routes (장바구니)
    # ==========================================
    
    @app.route('/api/cart', methods=['GET'])
    @login_required
    def get_cart():
        """장바구니 목록"""
        return jsonify(repository.get_cart_items(current_user.id))
    
    
    @app.route('/api/cart', methods=['POST'])
    @login_required
    def add_to_cart():
        """장바구니에 추가"""
        data = get_json_or_error()
        if not data or not data.get('book_id'):
            return jsonify({'error': 'Book ID required'}), 400
        return jsonify(repository.add_to_cart(current_user.id, data['book_id'])), 201
    
    
    @app.route('/api/cart/<int:item_id>', methods=['DELETE'])
    @login_required
    def remove_from_cart(item_id):
        """장바구니에서 제거"""
        if not repository.remove_from_cart(current_user.id, item_id):
            return jsonify({'error': 'Not found'}), 404
        return jsonify({'message': 'Removed'})
    
    
    @app.route('/api/cart/clear', methods=['DELETE'])
    @login_required
    def clear_cart():
        """장바구니 비우기"""
        repository.clear_cart(current_user.id)
        return jsonify({'message': 'Cart cleared'})
    
    
    @app.route('/api/checkout', methods=['POST'])
    @login_required
    def checkout():
        """결제 처리 (시뮬레이션)"""
        data = request.get_json()
        cart_items = repository.get_cart_items(current_user.id)
        
        if len(cart_items) == 0:
            return jsonify({'error': 'Cart is empty'}), 400
        
        total = 0
        for item in cart_items:
            total = total + (item.get('price', 0) * item.get('quantity', 1))
        
        order = repository.create_order(
            current_user.id, cart_items, total,
            data.get('card_last_four', '0000')
        )
        repository.clear_cart(current_user.id)
        
        return jsonify({'message': 'Order completed', 'order': order, 'total': total})
