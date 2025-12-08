# ==============================================
# Book Routes
# ==============================================

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

import repository

books_bp = Blueprint('books', __name__)


@books_bp.route('/tags', methods=['GET'])
def get_book_tags():
    """Get all book tags with their book counts."""
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
    
    for i in range(len(result)):
        for j in range(i + 1, len(result)):
            if result[j]['name'] < result[i]['name']:
                temp = result[i]
                result[i] = result[j]
                result[j] = temp
    
    return jsonify(result)


@books_bp.route('', methods=['GET'])
def get_books_by_tags():
    """Get books filtered by tags (AND logic)."""
    tag_slugs = request.args.getlist('tags')
    if not tag_slugs:
        tag_slugs = request.args.getlist('tags[]')
    
    limit = request.args.get('limit', 24, type=int)
    
    books = repository.get_books_by_tags(tag_slugs, limit)
    
    return jsonify(books)


@books_bp.route('/all', methods=['GET'])
def get_all_books():
    """Get all book recommendations."""
    return jsonify(repository.get_all_books())


@books_bp.route('/search', methods=['GET'])
def search_books():
    """Search books by title or author."""
    query = request.args.get('q', '')
    limit = request.args.get('limit', 24, type=int)
    
    if not query:
        return jsonify([])
    
    query_lower = query.lower()
    
    all_books = repository.get_all_books()
    result = []
    for book in all_books:
        title_lower = book['title'].lower()
        author_lower = book['author'].lower()
        
        title_match = query_lower in title_lower
        author_match = query_lower in author_lower
        
        if title_match or author_match:
            result.append(book)
    
    if len(result) > limit:
        result = result[:limit]
    
    return jsonify(result)


@books_bp.route('/favorites', methods=['GET'])
@login_required
def get_favorites():
    """Get all favorite books for the current user."""
    user = current_user
    favorite_ids = repository.get_user_book_favorites(user.id)
    
    all_books = repository.get_all_books()
    result = []
    for book_id in favorite_ids:
        for book in all_books:
            if book['id'] == book_id:
                book_copy = dict(book)
                book_copy['is_favorite'] = True
                result.append(book_copy)
                break
    
    return jsonify(result)


@books_bp.route('/favorites/ids', methods=['GET'])
@login_required
def get_favorite_ids():
    """Get list of favorite book IDs for the current user."""
    user = current_user
    favorite_ids = repository.get_user_book_favorites(user.id)
    return jsonify(favorite_ids)


@books_bp.route('/<int:book_id>/favorite', methods=['POST'])
@login_required
def add_to_favorites(book_id):
    """Add a book to favorites."""
    user = current_user
    success = repository.add_book_favorite(user.id, book_id)
    
    if success:
        return jsonify({'message': 'Added to favorites'})
    else:
        return jsonify({'message': 'Already in favorites'})


@books_bp.route('/<int:book_id>/favorite', methods=['DELETE'])
@login_required
def remove_from_favorites(book_id):
    """Remove a book from favorites."""
    user = current_user
    success = repository.remove_book_favorite(user.id, book_id)
    
    if success:
        return jsonify({'message': 'Removed from favorites'})
    else:
        return jsonify({'error': 'Not in favorites'}), 404
