import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import BookCard from '../components/BookCard';
import api from '../api/axios';
import { BookOpen, X } from 'lucide-react';

const Books = () => {
  const { user } = useAuth();
  const [selectedTags, setSelectedTags] = useState([]);
  const [books, setBooks] = useState([]);
  const [tags, setTags] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTags();
  }, []);

  useEffect(() => {
    fetchBooks();
  }, [selectedTags]);

  const fetchTags = async () => {
    try {
      const res = await api.get('/books/tags');
      setTags(res.data);
    } catch (err) {
      console.error('Failed to fetch tags:', err);
    }
  };

  const fetchBooks = async () => {
    setLoading(true);
    try {
      const params = {};
      if (selectedTags.length > 0) {
        params.tags = selectedTags;
      }
      const res = await api.get('/books', { params });
      setBooks(res.data);
    } catch (err) {
      console.error('Failed to fetch books:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleTag = (slug) => {
    setSelectedTags(prev => 
      prev.includes(slug) 
        ? prev.filter(t => t !== slug)
        : [...prev, slug]
    );
  };

  const clearAllTags = () => {
    setSelectedTags([]);
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
              style={{
                '--tag-color': tag.color,
                '--tag-bg': selectedTags.includes(tag.slug) ? tag.color : 'transparent'
              }}
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
                  ? `${books.length} books matching selected tags (sorted by relevance)`
                  : `All ${books.length} books`
                }
              </div>
              <div className="books-full-grid">
                {books.map((book) => (
                  <BookCard 
                    key={book.id} 
                    book={book} 
                    showTags={true} 
                    showScore={selectedTags.length > 0}
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
