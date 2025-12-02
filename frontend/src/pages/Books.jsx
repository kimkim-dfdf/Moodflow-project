import { useState, useEffect, useRef } from 'react';
import api from '../api/axios';
import { BookOpen, X } from 'lucide-react';

const BookCard = ({ book, showTags = false }) => (
  <div className="book-card">
    <div className="book-icon">
      <BookOpen size={24} />
    </div>
    <div className="book-info">
      <h4 className="book-title">{book.title}</h4>
      <p className="book-author">{book.author}</p>
      <span className="book-genre">{book.genre}</span>
      {book.description && (
        <p className="book-description">{book.description}</p>
      )}
      {showTags && book.tags && book.tags.length > 0 && (
        <div className="book-tags">
          {book.tags.map((tag) => (
            <span key={tag.id} className="book-tag-pill">
              {tag.name}
            </span>
          ))}
        </div>
      )}
    </div>
  </div>
);

const Books = () => {
  const [selectedTags, setSelectedTags] = useState([]);
  const [books, setBooks] = useState([]);
  const [tags, setTags] = useState([]);
  const [loading, setLoading] = useState(true);
  const fetchIdRef = useRef(0);

  useEffect(() => {
    const init = async () => {
      try {
        const res = await api.get('/books/tags');
        setTags(res.data);
      } catch (err) {
        console.error('Failed to fetch tags:', err);
      }
      fetchBooks([]);
    };
    init();
  }, []);

  const fetchBooks = async (tagList) => {
    const fetchId = ++fetchIdRef.current;
    setLoading(true);
    try {
      let url = '/books';
      if (tagList.length > 0) {
        const tagParams = tagList.map(t => `tags=${t}`).join('&');
        url = `/books?${tagParams}`;
      }
      const res = await api.get(url);
      if (fetchId === fetchIdRef.current) {
        setBooks(res.data);
      }
    } catch (err) {
      console.error('Failed to fetch books:', err);
    } finally {
      if (fetchId === fetchIdRef.current) {
        setLoading(false);
      }
    }
  };

  const toggleTag = (slug) => {
    const newTags = selectedTags.includes(slug)
      ? selectedTags.filter(t => t !== slug)
      : [...selectedTags, slug];
    setSelectedTags(newTags);
    fetchBooks(newTags);
  };

  const clearAllTags = () => {
    setSelectedTags([]);
    fetchBooks([]);
  };

  const getSelectedTagNames = () => {
    return selectedTags.map(slug => {
      const tag = tags.find(t => t.slug === slug);
      return tag ? tag.name : slug;
    });
  };

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
            <button className="clear-tags-btn" onClick={clearAllTags}>
              Clear All
            </button>
          )}
        </div>
        
        <div className="tag-chips-container">
          {tags.map((tag) => (
            <button
              key={tag.id}
              className={`tag-chip ${selectedTags.includes(tag.slug) ? 'active' : ''}`}
              onClick={() => toggleTag(tag.slug)}
            >
              {tag.name}
              <span className="tag-count">{tag.book_count}</span>
            </button>
          ))}
        </div>

        {selectedTags.length > 0 && (
          <div className="selected-tags-display">
            <span>Selected:</span>
            <div className="selected-tags-list">
              {getSelectedTagNames().map((name, idx) => (
                <span key={idx} className="selected-tag-pill">
                  {name}
                  <X 
                    size={14} 
                    onClick={() => toggleTag(selectedTags[idx])}
                    className="remove-tag-icon"
                  />
                </span>
              ))}
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
                {selectedTags.length > 0 
                  ? `${books.length} books found`
                  : `All ${books.length} books`
                }
              </div>
              <div className="books-full-grid">
                {books.map((book) => (
                  <BookCard 
                    key={book.id} 
                    book={book} 
                    showTags={true}
                  />
                ))}
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
};

export default Books;
