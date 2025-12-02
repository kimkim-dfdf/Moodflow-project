import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import BookCard from '../components/BookCard';
import api from '../api/axios';
import { BookOpen } from 'lucide-react';

const Books = () => {
  const { user } = useAuth();
  const [selectedEmotion, setSelectedEmotion] = useState('all');
  const [books, setBooks] = useState([]);
  const [emotions, setEmotions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEmotions();
  }, []);

  useEffect(() => {
    fetchBooks();
  }, [selectedEmotion]);

  const fetchEmotions = async () => {
    try {
      const res = await api.get('/emotions');
      setEmotions(res.data);
    } catch (err) {
      console.error('Failed to fetch emotions:', err);
    }
  };

  const fetchBooks = async () => {
    setLoading(true);
    try {
      if (selectedEmotion === 'all') {
        const allBooks = [];
        for (const emotion of emotions) {
          const res = await api.get('/books/recommendations', { 
            params: { emotion: emotion.name, limit: 4 } 
          });
          allBooks.push(...res.data);
        }
        setBooks(allBooks);
      } else {
        const res = await api.get('/books/recommendations', { 
          params: { emotion: selectedEmotion, limit: 10 } 
        });
        setBooks(res.data);
      }
    } catch (err) {
      console.error('Failed to fetch books:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (emotions.length > 0 && selectedEmotion === 'all') {
      fetchBooks();
    }
  }, [emotions]);

  return (
    <div className="books-page">
      <header className="page-header">
        <h1><BookOpen size={28} /> Book Recommendations</h1>
        <p>Discover books that match your current mood</p>
      </header>

      <div className="emotion-filter">
        <button 
          className={`filter-btn ${selectedEmotion === 'all' ? 'active' : ''}`}
          onClick={() => setSelectedEmotion('all')}
        >
          All Moods
        </button>
        {emotions.map((emotion) => (
          <button
            key={emotion.id}
            className={`filter-btn ${selectedEmotion === emotion.name ? 'active' : ''}`}
            onClick={() => setSelectedEmotion(emotion.name)}
          >
            {emotion.emoji} {emotion.name}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="loading-state">Loading book recommendations...</div>
      ) : (
        <div className="books-container">
          {books.length > 0 ? (
            <div className="books-full-grid">
              {books.map((book) => (
                <BookCard key={book.id} book={book} />
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <BookOpen size={48} />
              <p>No books found for this mood.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Books;
