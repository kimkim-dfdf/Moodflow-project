import { useState, useEffect, useRef } from 'react';
import api from '../api/axios';
import { BookOpen, X, Search, Heart, Star } from 'lucide-react';

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
        </div>
        
        <div className="modal-footer">
          <button 
            className={'modal-favorite-btn ' + (isFavorite ? 'active' : '')}
            onClick={handleFavoriteClick}
          >
            <Heart size={20} fill={isFavorite ? '#ef4444' : 'none'} />
            {isFavorite ? 'Remove from Favorites' : 'Add to Favorites'}
          </button>
        </div>
      </div>
    </div>
  );
}

function Books() {
  const [selectedTags, setSelectedTags] = useState([]);
  const [books, setBooks] = useState([]);
  const [tags, setTags] = useState([]);
  const [loading, setLoading] = useState(true);
  const [favoriteIds, setFavoriteIds] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [activeTab, setActiveTab] = useState('all');
  const [favoriteBooks, setFavoriteBooks] = useState([]);
  const [selectedBook, setSelectedBook] = useState(null);
  const fetchIdRef = useRef(0);
  const searchTimeoutRef = useRef(null);

  useEffect(function() {
    api.get('/books/tags').then(function(res) {
      setTags(res.data);
    });
    fetchBooks([]);
    fetchFavoriteIds();
  }, []);

  function fetchFavoriteIds() {
    api.get('/books/favorites/ids').then(function(res) {
      setFavoriteIds(res.data);
    }).catch(function() {
      setFavoriteIds([]);
    });
  }

  function fetchFavorites() {
    setLoading(true);
    api.get('/books/favorites').then(function(res) {
      setFavoriteBooks(res.data);
      setLoading(false);
    }).catch(function() {
      setFavoriteBooks([]);
      setLoading(false);
    });
  }

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
    
    if (isFav) {
      api.delete('/books/' + bookId + '/favorite').then(function() {
        var newIds = favoriteIds.filter(function(id) { return id !== bookId; });
        setFavoriteIds(newIds);
        if (activeTab === 'favorites') {
          fetchFavorites();
        }
      });
    } else {
      api.post('/books/' + bookId + '/favorite').then(function() {
        var newIds = favoriteIds.concat([bookId]);
        setFavoriteIds(newIds);
      });
    }
  }

  function isFavorite(bookId) {
    return favoriteIds.indexOf(bookId) >= 0;
  }

  function handleTabChange(tab) {
    setActiveTab(tab);
    setSearchQuery('');
    setSearchResults([]);
    
    if (tab === 'favorites') {
      fetchFavorites();
    } else {
      fetchBooks(selectedTags);
    }
  }

  function openBookDetail(book) {
    setSelectedBook(book);
  }

  function closeBookDetail() {
    setSelectedBook(null);
  }

  function getDisplayBooks() {
    if (searchQuery.trim()) {
      return searchResults;
    }
    if (activeTab === 'favorites') {
      return favoriteBooks;
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
        />
      )}
    </div>
  );
}

export default Books;
