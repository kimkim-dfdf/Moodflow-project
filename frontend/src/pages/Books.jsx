import { useState, useEffect, useRef } from 'react';
import api from '../api/axios';
import { BookOpen, X, BookMarked, BookCheck, Clock } from 'lucide-react';

function BookCard(props) {
  var book = props.book;
  var showTags = props.showTags || false;
  var readingStatus = props.readingStatus;
  var onStatusChange = props.onStatusChange;
  var onProgressChange = props.onProgressChange;
  
  function getStatusLabel(status) {
    if (status === 'want_to_read') {
      return 'Want to Read';
    }
    if (status === 'reading') {
      return 'Reading';
    }
    if (status === 'completed') {
      return 'Completed';
    }
    return 'Not Set';
  }
  
  function getStatusIcon(status) {
    if (status === 'want_to_read') {
      return <Clock size={14} />;
    }
    if (status === 'reading') {
      return <BookMarked size={14} />;
    }
    if (status === 'completed') {
      return <BookCheck size={14} />;
    }
    return <BookOpen size={14} />;
  }
  
  function getStatusClass(status) {
    if (status === 'want_to_read') {
      return 'status-want';
    }
    if (status === 'reading') {
      return 'status-reading';
    }
    if (status === 'completed') {
      return 'status-completed';
    }
    return 'status-none';
  }
  
  function handleStatusSelect(e) {
    var newStatus = e.target.value;
    if (newStatus === 'none') {
      onStatusChange(book.id, null);
    } else {
      onStatusChange(book.id, newStatus);
    }
  }
  
  function handleProgressChange(e) {
    var newProgress = parseInt(e.target.value, 10);
    onProgressChange(book.id, newProgress);
  }
  
  var currentStatus = readingStatus ? readingStatus.status : null;
  var currentProgress = readingStatus ? readingStatus.progress : 0;
  
  return (
    <div className={'book-card ' + getStatusClass(currentStatus)}>
      <div className="book-icon"><BookOpen size={24} /></div>
      <div className="book-info">
        <h4 className="book-title">{book.title}</h4>
        <p className="book-author">{book.author}</p>
        <span className="book-genre">{book.genre}</span>
        {book.description && <p className="book-description">{book.description}</p>}
        {showTags && book.tags && book.tags.length > 0 && (
          <div className="book-tags">
            {book.tags.map(function(tag) {
              return <span key={tag.id} className="book-tag-pill">{tag.name}</span>;
            })}
          </div>
        )}
        
        <div className="reading-status-section">
          <div className="reading-status-selector">
            <span className="reading-status-label">
              {getStatusIcon(currentStatus)}
              Reading Status:
            </span>
            <select 
              className={'reading-status-dropdown ' + getStatusClass(currentStatus)}
              value={currentStatus || 'none'}
              onChange={handleStatusSelect}
            >
              <option value="none">-- Select --</option>
              <option value="want_to_read">Want to Read</option>
              <option value="reading">Reading</option>
              <option value="completed">Completed</option>
            </select>
          </div>
          
          {currentStatus === 'reading' && (
            <div className="reading-progress-section">
              <div className="progress-header">
                <span>Progress: {currentProgress}%</span>
              </div>
              <div className="progress-bar-container">
                <div 
                  className="progress-bar-fill" 
                  style={{ width: currentProgress + '%' }}
                ></div>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={currentProgress}
                onChange={handleProgressChange}
                className="progress-slider"
              />
            </div>
          )}
          
          {currentStatus === 'completed' && (
            <div className="completed-badge">
              <BookCheck size={16} />
              <span>Completed!</span>
            </div>
          )}
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
  const [readingStatuses, setReadingStatuses] = useState({});
  const fetchIdRef = useRef(0);

  useEffect(function() {
    api.get('/books/tags').then(function(res) {
      setTags(res.data);
    });
    fetchBooks([]);
    fetchReadingStatuses();
  }, []);

  function fetchReadingStatuses() {
    api.get('/books/reading-status').then(function(res) {
      var statusMap = {};
      for (var i = 0; i < res.data.length; i++) {
        var entry = res.data[i];
        statusMap[entry.book_id] = entry;
      }
      setReadingStatuses(statusMap);
    }).catch(function(err) {
      console.log('Could not fetch reading statuses:', err);
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

  function handleStatusChange(bookId, status) {
    if (status === null) {
      api.delete('/books/' + bookId + '/reading-status').then(function() {
        var newStatuses = Object.assign({}, readingStatuses);
        delete newStatuses[bookId];
        setReadingStatuses(newStatuses);
      }).catch(function(err) {
        console.log('Could not delete reading status:', err);
      });
    } else {
      var progress = 0;
      if (status === 'completed') {
        progress = 100;
      } else if (status === 'reading') {
        var existing = readingStatuses[bookId];
        if (existing && existing.progress > 0 && existing.progress < 100) {
          progress = existing.progress;
        }
      }
      
      api.post('/books/' + bookId + '/reading-status', {
        status: status,
        progress: progress
      }).then(function(res) {
        var newStatuses = Object.assign({}, readingStatuses);
        newStatuses[bookId] = res.data;
        setReadingStatuses(newStatuses);
      }).catch(function(err) {
        console.log('Could not save reading status:', err);
      });
    }
  }

  function handleProgressChange(bookId, progress) {
    var existing = readingStatuses[bookId];
    if (!existing) {
      return;
    }
    
    api.post('/books/' + bookId + '/reading-status', {
      status: existing.status,
      progress: progress
    }).then(function(res) {
      var newStatuses = Object.assign({}, readingStatuses);
      newStatuses[bookId] = res.data;
      setReadingStatuses(newStatuses);
    }).catch(function(err) {
      console.log('Could not update progress:', err);
    });
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

  return (
    <div className="books-page">
      <header className="page-header">
        <h1><BookOpen size={28} /> Book Recommendations</h1>
        <p>Discover books that match your current mood</p>
      </header>

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

      {loading ? (
        <div className="loading-state">Loading books...</div>
      ) : (
        <div className="books-container">
          {books.length > 0 ? (
            <>
              <div className="books-result-info">
                {selectedTags.length > 0 ? books.length + ' books found' : 'All ' + books.length + ' books'}
              </div>
              <div className="books-full-grid">
                {books.map(function(book) {
                  return (
                    <BookCard 
                      key={book.id} 
                      book={book} 
                      showTags={true}
                      readingStatus={readingStatuses[book.id]}
                      onStatusChange={handleStatusChange}
                      onProgressChange={handleProgressChange}
                    />
                  );
                })}
              </div>
            </>
          ) : (
            <div className="empty-state">
              <BookOpen size={48} />
              <p>No books found for selected tags.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default Books;
