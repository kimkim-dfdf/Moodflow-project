# ==============================================
# Book Repository
# ==============================================
# Handles all book-related database operations
# ==============================================

from models import Book, BookTag


def get_all_book_tags():
    """Get all available book tags."""
    tags = BookTag.query.all()
    
    result = []
    for tag in tags:
        result.append(tag.to_dict())
    
    return result


def get_tag_by_slug(slug):
    """Find a tag by its slug."""
    tag = BookTag.query.filter_by(slug=slug).first()
    if tag:
        return tag.to_dict()
    return None


def get_all_books():
    """Get all books from database."""
    books = Book.query.all()
    tags_cache = get_all_tags_as_dict()
    
    result = []
    for book in books:
        book_dict = book.to_dict()
        book_dict['tags'] = get_tag_objects_for_book(book_dict, tags_cache)
        result.append(book_dict)
    
    return result


def get_books_by_tags(tag_slugs, limit):
    """
    Get books that match ALL of the specified tags (AND logic).
    """
    books = Book.query.all()
    tags_cache = get_all_tags_as_dict()
    
    if not tag_slugs:
        result = []
        for book in books:
            book_dict = book.to_dict()
            book_dict['tags'] = get_tag_objects_for_book(book_dict, tags_cache)
            result.append(book_dict)
        
        if limit and limit < len(result):
            return result[:limit]
        return result
    
    result = []
    
    for book in books:
        book_tags = book.tags.split(',') if book.tags else []
        
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


def get_all_tags_as_dict():
    """
    Get all book tags as a dictionary for fast lookup.
    Key: slug, Value: tag dictionary
    """
    all_tags = BookTag.query.all()
    
    result = {}
    for tag in all_tags:
        result[tag.slug] = tag.to_dict()
    
    return result


def get_tag_objects_for_book(book_dict, tags_cache=None):
    """
    Get full tag objects for a book's tags.
    Converts tag slugs to full tag dictionaries.
    Uses cache to avoid N+1 queries.
    """
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
