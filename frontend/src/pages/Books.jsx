import { useState, useEffect, useRef } from 'react';
import api from '../api/axios';
import { BookOpen, X, Search, Heart, Share2, Star, Trash2, User } from 'lucide-react';

function BookCard(props) {
  var book = props.book;
  var showTags = props.showTags || false;
  var isFavorite = props.isFavorite || false;
  var onToggleFavorite = props.onToggleFavorite;
  var onOpenDetail = props.onOpenDetail;
  
  function handleFavoriteClick(e) {
    e.stopPropagation();
    if (onToggleFavorite) {
      onToggleFavorite(book.id);
    }
  }
  
  function handleCardClick() {
    if (onOpenDetail) {
      onOpenDetail(book);
    }
  }
  
  return (
    <div className="book-card" onClick={handleCardClick}>
      <div className="book-icon"><BookOpen size={24} /></div>
      <div className="book-info">
        <div className="book-title-row">
          <h4 className="book-title">{book.title}</h4>
          <button 
            className={'favorite-btn ' + (isFavorite ? 'active' : '')} 
            onClick={handleFavoriteClick}
            title={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
          >
            <Heart size={18} fill={isFavorite ? '#ef4444' : 'none'} />
          </button>
        </div>
        <p className="book-author">{book.author}</p>
        <span className="book-genre">{book.genre}</span>
        {showTags && book.tags && book.tags.length > 0 && (
          <div className="book-tags">
            {book.tags.map(function(tag) {
              return <span key={tag.id} className="book-tag-pill">{tag.name}</span>;
            })}
          </div>
        )}
      </div>
    </div>
  );
}

function BookDetailModal(props) {
  var book = props.book;
  var onClose = props.onClose;
  var isFavorite = props.isFavorite;
  var onToggleFavorite = props.onToggleFavorite;
  var currentUserId = props.currentUserId;
  var [shareMessage, setShareMessage] = useState('');
  var [reviews, setReviews] = useState([]);
  var [reviewRating, setReviewRating] = useState(5);
  var [reviewContent, setReviewContent] = useState('');
  var [isSubmitting, setIsSubmitting] = useState(false);
  var [reviewError, setReviewError] = useState('');
  var [hasUserReview, setHasUserReview] = useState(false);
  
  useEffect(function() {
    if (book) {
      loadReviews();
    }
  }, [book]);
  
  function loadReviews() {
    api.get('/books/' + book.id + '/reviews').then(function(res) {
      setReviews(res.data);
      var userHasReview = false;
      for (var i = 0; i < res.data.length; i++) {
        if (res.data[i].user_id === currentUserId) {
          userHasReview = true;
          break;
        }
      }
      setHasUserReview(userHasReview);
    }).catch(function() {
      setReviews([]);
    });
  }
  
  if (!book) {
    return null;
  }
  
  function handleOverlayClick(e) {
    if (e.target.className === 'modal-overlay') {
      onClose();
    }
  }
  
  function handleFavoriteClick() {
    if (onToggleFavorite) {
      onToggleFavorite(book.id);
    }
  }
  
  function handleShareClick() {
    var shareText = 'Check out this book I found on MoodFlow!\n\n';
    shareText = shareText + book.title + ' by ' + book.author + '\n';
    shareText = shareText + 'Genre: ' + book.genre + '\n';
    if (book.description) {
      shareText = shareText + '\n' + book.description;
    }
    
    if (navigator.share) {
      navigator.share({
        title: book.title,
        text: shareText
      }).catch(function(error) {
        console.log('Share cancelled');
      });
    } else {
      navigator.clipboard.writeText(shareText).then(function() {
        setShareMessage('Copied to clipboard!');
        setTimeout(function() {
          setShareMessage('');
        }, 2000);
      }).catch(function() {
        setShareMessage('Failed to copy');
        setTimeout(function() {
          setShareMessage('');
        }, 2000);
      });
    }
  }
  
  function handleSubmitReview() {
    if (!reviewContent.trim()) {
      setReviewError('Please write a review');
      return;
    }
    
    setIsSubmitting(true);
    setReviewError('');
    
    api.post('/books/' + book.id + '/reviews', {
      rating: reviewRating,
      content: reviewContent
    }).then(function(res) {
      setReviews([res.data].concat(reviews));
      setReviewContent('');
      setReviewRating(5);
      setHasUserReview(true);
      setIsSubmitting(false);
    }).catch(function(err) {
      var message = 'Failed to submit review';
      if (err.response && err.response.data && err.response.data.error) {
        message = err.response.data.error;
      }
      setReviewError(message);
      setIsSubmitting(false);
    });
  }
  
  function handleDeleteReview(reviewId) {
    api.delete('/books/reviews/' + reviewId).then(function() {
      var newReviews = [];
      for (var i = 0; i < reviews.length; i++) {
        if (reviews[i].id !== reviewId) {
          newReviews.push(reviews[i]);
        }
      }
      setReviews(newReviews);
      setHasUserReview(false);
    }).catch(function() {
      setReviewError('Failed to delete review');
    });
  }
  
  function renderStars(rating, interactive) {
    var stars = [];
    for (var i = 1; i <= 5; i++) {
      if (interactive) {
        var starIndex = i;
        stars.push(
          <button 
            key={i} 
            type="button"
            className="star-btn"
            onClick={function() { setReviewRating(starIndex); }.bind(null, starIndex)}
          >
            <Star size={20} fill={i <= reviewRating ? '#fbbf24' : 'none'} color={i <= reviewRating ? '#fbbf24' : '#d1d5db'} />
          </button>
        );
      } else {
        stars.push(
          <Star key={i} size={16} fill={i <= rating ? '#fbbf24' : 'none'} color={i <= rating ? '#fbbf24' : '#d1d5db'} />
        );
      }
    }
    return stars;
  }
  
  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="book-detail-modal">
        <button className="modal-close-btn" onClick={onClose}>
          <X size={24} />
        </button>
        
        <div className="modal-header">
          <div className="modal-book-icon">
            <BookOpen size={48} />
          </div>
          <div className="modal-title-section">
            <h2>{book.title}</h2>
            <p className="modal-author">{book.author}</p>
          </div>
        </div>
        
        <div className="modal-body">
          <div className="modal-meta">
            <span className="modal-genre">{book.genre}</span>
            {book.emotion && (
              <span className="modal-emotion">Recommended for: {book.emotion}</span>
            )}
          </div>
          
          {book.description && (
            <div className="modal-description">
              <h4>Description</h4>
              <p>{book.description}</p>
            </div>
          )}
          
          {book.tags && book.tags.length > 0 && (
            <div className="modal-tags">
              <h4>Mood Tags</h4>
              <div className="modal-tags-list">
                {book.tags.map(function(tag) {
                  return (
                    <span 
                      key={tag.id} 
                      className="modal-tag-pill"
                      style={{ backgroundColor: tag.color || '#6B7280' }}
                    >
                      {tag.name}
                    </span>
                  );
                })}
              </div>
            </div>
          )}
          
          <div className="modal-reviews">
            <h4>Reviews ({reviews.length})</h4>
            
            {!hasUserReview && currentUserId && (
              <div className="review-form">
                <div className="review-rating-input">
                  <span>Your Rating:</span>
                  <div className="stars-input">{renderStars(reviewRating, true)}</div>
                </div>
                <textarea
                  className="review-textarea"
                  placeholder="Write your review..."
                  value={reviewContent}
                  onChange={function(e) { setReviewContent(e.target.value); }}
                  rows={3}
                />
                {reviewError && <div className="review-error">{reviewError}</div>}
                <button 
                  className="review-submit-btn"
                  onClick={handleSubmitReview}
                  disabled={isSubmitting}
                >
                  {isSubmitting ? 'Submitting...' : 'Submit Review'}
                </button>
              </div>
            )}
            
            {hasUserReview && (
              <div className="review-notice">You have already reviewed this book.</div>
            )}
            
            <div className="reviews-list">
              {reviews.length === 0 ? (
                <p className="no-reviews">No reviews yet. Be the first to review!</p>
              ) : (
                reviews.map(function(review) {
                  return (
                    <div key={review.id} className="review-item">
                      <div className="review-header">
                        <div className="review-user">
                          <User size={16} />
                          <span>{review.username}</span>
                        </div>
                        <div className="review-stars">{renderStars(review.rating, false)}</div>
                        {review.user_id === currentUserId && (
                          <button 
                            className="review-delete-btn"
                            onClick={function() { handleDeleteReview(review.id); }}
                            title="Delete review"
                          >
                            <Trash2 size={16} />
                          </button>
                        )}
                      </div>
                      <p className="review-content">{review.content}</p>
                      <span className="review-date">
                        {new Date(review.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
        
        <div className="modal-footer">
          <button 
            className={'modal-favorite-btn ' + (isFavorite ? 'active' : '')}
            onClick={handleFavoriteClick}
          >
            <Heart size={20} fill={isFavorite ? '#ef4444' : 'none'} />
            {isFavorite ? 'Remove from Favorites' : 'Add to Favorites'}
          </button>
          <button 
            className="modal-share-btn"
            onClick={handleShareClick}
          >
            <Share2 size={20} />
            Share with Friends
          </button>
        </div>
        {shareMessage && (
          <div className="share-message">{shareMessage}</div>
        )}
      </div>
    </div>
  );
}

function getFavoritesFromStorage() {
  try {
    var stored = localStorage.getItem('book_favorites');
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (e) {
  }
  return [];
}

function saveFavoritesToStorage(favoriteIds) {
  try {
    localStorage.setItem('book_favorites', JSON.stringify(favoriteIds));
  } catch (e) {
  }
}

function Books() {
  const [selectedTags, setSelectedTags] = useState([]);
  const [books, setBooks] = useState([]);
  const [tags, setTags] = useState([]);
  const [loading, setLoading] = useState(true);
  const [favoriteIds, setFavoriteIds] = useState(getFavoritesFromStorage());
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [activeTab, setActiveTab] = useState('all');
  const [allBooks, setAllBooks] = useState([]);
  const [selectedBook, setSelectedBook] = useState(null);
  const [currentUserId, setCurrentUserId] = useState(null);
  const fetchIdRef = useRef(0);
  const searchTimeoutRef = useRef(null);

  useEffect(function() {
    api.get('/books/tags').then(function(res) {
      setTags(res.data);
    });
    api.get('/books').then(function(res) {
      setAllBooks(res.data);
    });
    api.get('/auth/me').then(function(res) {
      setCurrentUserId(res.data.id);
    }).catch(function() {
      setCurrentUserId(null);
    });
    fetchBooks([]);
  }, []);

  function fetchBooks(tagList) {
    var fetchId = ++fetchIdRef.current;
    setLoading(true);
    
    var url = '/books';
    if (tagList.length > 0) {
      var params = [];
      for (var i = 0; i < tagList.length; i++) {
        params.push('tags=' + tagList[i]);
      }
      url = '/books?' + params.join('&');
    }
    
    api.get(url).then(function(res) {
      if (fetchId === fetchIdRef.current) {
        setBooks(res.data);
        setLoading(false);
      }
    }).catch(function() {
      if (fetchId === fetchIdRef.current) {
        setLoading(false);
      }
    });
  }

  function handleSearch(query) {
    setSearchQuery(query);
    
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }
    
    if (!query.trim()) {
      setSearchResults([]);
      setIsSearching(false);
      return;
    }
    
    setIsSearching(true);
    
    searchTimeoutRef.current = setTimeout(function() {
      api.get('/books/search?q=' + encodeURIComponent(query)).then(function(res) {
        setSearchResults(res.data);
        setIsSearching(false);
      }).catch(function() {
        setSearchResults([]);
        setIsSearching(false);
      });
    }, 300);
  }

  function clearSearch() {
    setSearchQuery('');
    setSearchResults([]);
    setIsSearching(false);
  }

  function toggleTag(slug) {
    var newTags;
    if (selectedTags.indexOf(slug) >= 0) {
      newTags = selectedTags.filter(function(t) { return t !== slug; });
    } else {
      newTags = selectedTags.concat([slug]);
    }
    setSelectedTags(newTags);
    fetchBooks(newTags);
  }

  function clearAllTags() {
    setSelectedTags([]);
    fetchBooks([]);
  }

  function getSelectedTagNames() {
    var names = [];
    for (var i = 0; i < selectedTags.length; i++) {
      var slug = selectedTags[i];
      for (var j = 0; j < tags.length; j++) {
        if (tags[j].slug === slug) {
          names.push(tags[j].name);
          break;
        }
      }
    }
    return names;
  }

  function toggleFavorite(bookId) {
    var isFav = favoriteIds.indexOf(bookId) >= 0;
    var newIds;
    
    if (isFav) {
      newIds = favoriteIds.filter(function(id) { return id !== bookId; });
    } else {
      newIds = favoriteIds.concat([bookId]);
    }
    
    setFavoriteIds(newIds);
    saveFavoritesToStorage(newIds);
  }

  function isFavorite(bookId) {
    return favoriteIds.indexOf(bookId) >= 0;
  }

  function handleTabChange(tab) {
    setActiveTab(tab);
    setSearchQuery('');
    setSearchResults([]);
    
    if (tab === 'all') {
      fetchBooks(selectedTags);
    }
  }

  function openBookDetail(book) {
    setSelectedBook(book);
  }

  function closeBookDetail() {
    setSelectedBook(null);
  }

  function getFavoriteBooks() {
    var result = [];
    for (var i = 0; i < allBooks.length; i++) {
      var book = allBooks[i];
      if (favoriteIds.indexOf(book.id) >= 0) {
        result.push(book);
      }
    }
    return result;
  }

  function getDisplayBooks() {
    if (searchQuery.trim()) {
      return searchResults;
    }
    if (activeTab === 'favorites') {
      return getFavoriteBooks();
    }
    return books;
  }

  var displayBooks = getDisplayBooks();

  return (
    <div className="books-page">
      <header className="page-header">
        <h1><BookOpen size={28} /> Book Recommendations</h1>
        <p>Discover books that match your current mood</p>
      </header>

      <div className="books-search-section">
        <div className="search-input-wrapper">
          <Search size={20} className="search-icon" />
          <input
            type="text"
            className="books-search-input"
            placeholder="Search by title or author..."
            value={searchQuery}
            onChange={function(e) { handleSearch(e.target.value); }}
          />
          {searchQuery && (
            <button className="search-clear-btn" onClick={clearSearch}>
              <X size={18} />
            </button>
          )}
        </div>
      </div>

      <div className="books-tabs">
        <button 
          className={'books-tab ' + (activeTab === 'all' ? 'active' : '')}
          onClick={function() { handleTabChange('all'); }}
        >
          <BookOpen size={18} />
          All Books
        </button>
        <button 
          className={'books-tab ' + (activeTab === 'favorites' ? 'active' : '')}
          onClick={function() { handleTabChange('favorites'); }}
        >
          <Heart size={18} />
          Favorites ({favoriteIds.length})
        </button>
      </div>

      {activeTab === 'all' && !searchQuery && (
        <div className="tag-filter-section">
          <div className="tag-filter-header">
            <span className="tag-filter-label">Filter by Mood Tags</span>
            {selectedTags.length > 0 && (
              <button className="clear-tags-btn" onClick={clearAllTags}>Clear All</button>
            )}
          </div>
          
          <div className="tag-chips-container">
            {tags.map(function(tag) {
              var isActive = selectedTags.indexOf(tag.slug) >= 0;
              return (
                <button key={tag.id} className={'tag-chip ' + (isActive ? 'active' : '')} onClick={function() { toggleTag(tag.slug); }}>
                  {tag.name}
                  <span className="tag-count">{tag.book_count}</span>
                </button>
              );
            })}
          </div>

          {selectedTags.length > 0 && (
            <div className="selected-tags-display">
              <span>Selected:</span>
              <div className="selected-tags-list">
                {getSelectedTagNames().map(function(name, idx) {
                  return (
                    <span key={idx} className="selected-tag-pill">
                      {name}
                      <X size={14} onClick={function() { toggleTag(selectedTags[idx]); }} className="remove-tag-icon" />
                    </span>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {loading || isSearching ? (
        <div className="loading-state">Loading books...</div>
      ) : (
        <div className="books-container">
          {displayBooks.length > 0 ? (
            <>
              <div className="books-result-info">
                {searchQuery ? (
                  displayBooks.length + ' search results for "' + searchQuery + '"'
                ) : activeTab === 'favorites' ? (
                  displayBooks.length + ' favorite books'
                ) : selectedTags.length > 0 ? (
                  displayBooks.length + ' books found'
                ) : (
                  'All ' + displayBooks.length + ' books'
                )}
              </div>
              <div className="books-full-grid">
                {displayBooks.map(function(book) {
                  return (
                    <BookCard 
                      key={book.id} 
                      book={book} 
                      showTags={true}
                      isFavorite={isFavorite(book.id)}
                      onToggleFavorite={toggleFavorite}
                      onOpenDetail={openBookDetail}
                    />
                  );
                })}
              </div>
            </>
          ) : (
            <div className="empty-state">
              <BookOpen size={48} />
              {searchQuery ? (
                <p>No books found for "{searchQuery}"</p>
              ) : activeTab === 'favorites' ? (
                <p>No favorite books yet. Click the heart icon to add books to your favorites!</p>
              ) : (
                <p>No books found for selected tags.</p>
              )}
            </div>
          )}
        </div>
      )}

      {selectedBook && (
        <BookDetailModal
          book={selectedBook}
          onClose={closeBookDetail}
          isFavorite={isFavorite(selectedBook.id)}
          onToggleFavorite={toggleFavorite}
          currentUserId={currentUserId}
        />
      )}
    </div>
  );
}

export default Books;
