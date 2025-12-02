import { useState, useEffect, useRef } from 'react';
import api from '../api/axios';
import { BookOpen, X } from 'lucide-react';

function BookCard(props) {
  var book = props.book;
  var showTags = props.showTags || false;
  
  return (
    <div className="book-card">
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
      </div>
    </div>
  );
}

function Books() {
  const [selectedTags, setSelectedTags] = useState([]);
  const [books, setBooks] = useState([]);
  const [tags, setTags] = useState([]);
  const [loading, setLoading] = useState(true);
  const fetchIdRef = useRef(0);

  useEffect(function() {
    api.get('/books/tags').then(function(res) {
      setTags(res.data);
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
                  return <BookCard key={book.id} book={book} showTags={true} />;
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
