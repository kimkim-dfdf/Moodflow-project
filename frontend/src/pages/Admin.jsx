import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';
import { 
  BarChart3, Music, BookOpen, Users, CheckCircle2, 
  Heart, Plus, Edit2, Trash2, X, Save
} from 'lucide-react';

const Admin = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('statistics');
  const [loading, setLoading] = useState(true);
  
  const [statistics, setStatistics] = useState(null);
  const [musicList, setMusicList] = useState([]);
  const [booksList, setBooksList] = useState([]);
  const [emotions, setEmotions] = useState([]);
  const [tags, setTags] = useState([]);
  
  const [showMusicModal, setShowMusicModal] = useState(false);
  const [showBookModal, setShowBookModal] = useState(false);
  const [editingMusic, setEditingMusic] = useState(null);
  const [editingBook, setEditingBook] = useState(null);
  
  const [musicForm, setMusicForm] = useState({
    title: '',
    artist: '',
    genre: '',
    emotion_id: '',
    youtube_url: '',
    thumbnail_url: '',
    popularity_score: 0
  });
  
  const [bookForm, setBookForm] = useState({
    title: '',
    author: '',
    genre: '',
    emotion_id: '',
    description: '',
    cover_url: '',
    popularity_score: 0,
    tag_ids: []
  });

  useEffect(() => {
    if (!user?.is_admin) {
      navigate('/dashboard');
      return;
    }
    fetchData();
  }, [user, navigate]);

  useEffect(() => {
    if (activeTab === 'statistics' && !statistics) {
      fetchStatistics();
    } else if (activeTab === 'music' && musicList.length === 0) {
      fetchMusic();
    } else if (activeTab === 'books' && booksList.length === 0) {
      fetchBooks();
    }
  }, [activeTab]);

  const fetchData = async () => {
    try {
      const [emotionsRes, tagsRes] = await Promise.all([
        api.get('/emotions'),
        api.get('/books/tags')
      ]);
      setEmotions(emotionsRes.data);
      setTags(tagsRes.data);
      await fetchStatistics();
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStatistics = async () => {
    try {
      const res = await api.get('/admin/statistics');
      setStatistics(res.data);
    } catch (error) {
      console.error('Failed to fetch statistics:', error);
    }
  };

  const fetchMusic = async () => {
    try {
      const res = await api.get('/admin/music');
      setMusicList(res.data);
    } catch (error) {
      console.error('Failed to fetch music:', error);
    }
  };

  const fetchBooks = async () => {
    try {
      const res = await api.get('/admin/books');
      setBooksList(res.data);
    } catch (error) {
      console.error('Failed to fetch books:', error);
    }
  };

  const handleAddMusic = () => {
    setEditingMusic(null);
    setMusicForm({
      title: '',
      artist: '',
      genre: '',
      emotion_id: emotions[0]?.id || '',
      youtube_url: '',
      thumbnail_url: '',
      popularity_score: 0
    });
    setShowMusicModal(true);
  };

  const handleEditMusic = (music) => {
    setEditingMusic(music);
    setMusicForm({
      title: music.title,
      artist: music.artist || '',
      genre: music.genre || '',
      emotion_id: music.emotion_id,
      youtube_url: music.youtube_url || '',
      thumbnail_url: music.thumbnail_url || '',
      popularity_score: music.popularity_score || 0
    });
    setShowMusicModal(true);
  };

  const handleSaveMusic = async () => {
    try {
      if (editingMusic) {
        await api.put(`/admin/music/${editingMusic.id}`, musicForm);
      } else {
        await api.post('/admin/music', musicForm);
      }
      setShowMusicModal(false);
      fetchMusic();
    } catch (error) {
      console.error('Failed to save music:', error);
    }
  };

  const handleDeleteMusic = async (musicId) => {
    if (!window.confirm('Are you sure you want to delete this music?')) return;
    try {
      await api.delete(`/admin/music/${musicId}`);
      fetchMusic();
    } catch (error) {
      console.error('Failed to delete music:', error);
    }
  };

  const handleAddBook = () => {
    setEditingBook(null);
    setBookForm({
      title: '',
      author: '',
      genre: '',
      emotion_id: emotions[0]?.id || '',
      description: '',
      cover_url: '',
      popularity_score: 0,
      tag_ids: []
    });
    setShowBookModal(true);
  };

  const handleEditBook = (book) => {
    setEditingBook(book);
    setBookForm({
      title: book.title,
      author: book.author || '',
      genre: book.genre || '',
      emotion_id: book.emotion_id,
      description: book.description || '',
      cover_url: book.cover_url || '',
      popularity_score: book.popularity_score || 0,
      tag_ids: book.tags?.map(t => t.id) || []
    });
    setShowBookModal(true);
  };

  const handleSaveBook = async () => {
    try {
      if (editingBook) {
        await api.put(`/admin/books/${editingBook.id}`, bookForm);
      } else {
        await api.post('/admin/books', bookForm);
      }
      setShowBookModal(false);
      fetchBooks();
    } catch (error) {
      console.error('Failed to save book:', error);
    }
  };

  const handleDeleteBook = async (bookId) => {
    if (!window.confirm('Are you sure you want to delete this book?')) return;
    try {
      await api.delete(`/admin/books/${bookId}`);
      fetchBooks();
    } catch (error) {
      console.error('Failed to delete book:', error);
    }
  };

  const handleTagToggle = (tagId) => {
    setBookForm(prev => ({
      ...prev,
      tag_ids: prev.tag_ids.includes(tagId)
        ? prev.tag_ids.filter(id => id !== tagId)
        : [...prev.tag_ids, tagId]
    }));
  };

  if (loading) {
    return <div className="loading-screen">Loading admin dashboard...</div>;
  }

  if (!user?.is_admin) {
    return null;
  }

  return (
    <div className="admin-page">
      <header className="page-header">
        <h1>Admin Dashboard</h1>
      </header>

      <div className="admin-tabs">
        <button 
          className={`tab-btn ${activeTab === 'statistics' ? 'active' : ''}`}
          onClick={() => setActiveTab('statistics')}
        >
          <BarChart3 size={18} />
          Statistics
        </button>
        <button 
          className={`tab-btn ${activeTab === 'music' ? 'active' : ''}`}
          onClick={() => setActiveTab('music')}
        >
          <Music size={18} />
          Music
        </button>
        <button 
          className={`tab-btn ${activeTab === 'books' ? 'active' : ''}`}
          onClick={() => setActiveTab('books')}
        >
          <BookOpen size={18} />
          Books
        </button>
      </div>

      <div className="admin-content">
        {activeTab === 'statistics' && statistics && (
          <div className="statistics-tab">
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon users">
                  <Users size={24} />
                </div>
                <div className="stat-info">
                  <span className="stat-value">{statistics.total_users}</span>
                  <span className="stat-label">Total Users</span>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon tasks">
                  <CheckCircle2 size={24} />
                </div>
                <div className="stat-info">
                  <span className="stat-value">{statistics.total_tasks}</span>
                  <span className="stat-label">Total Tasks</span>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon emotions">
                  <Heart size={24} />
                </div>
                <div className="stat-info">
                  <span className="stat-value">{statistics.total_emotions}</span>
                  <span className="stat-label">Emotion Logs</span>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon music">
                  <Music size={24} />
                </div>
                <div className="stat-info">
                  <span className="stat-value">{statistics.total_music}</span>
                  <span className="stat-label">Music Items</span>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon books">
                  <BookOpen size={24} />
                </div>
                <div className="stat-info">
                  <span className="stat-value">{statistics.total_books}</span>
                  <span className="stat-label">Book Items</span>
                </div>
              </div>
            </div>

            <div className="admin-sections">
              <section className="card">
                <h3>Recent Users</h3>
                <div className="recent-users-list">
                  {statistics.recent_users?.map(user => (
                    <div key={user.id} className="user-item">
                      <div className="user-avatar-small">{user.username?.[0]?.toUpperCase()}</div>
                      <div className="user-details">
                        <span className="user-name">{user.username}</span>
                        <span className="user-email">{user.email}</span>
                      </div>
                      <span className="user-date">
                        {new Date(user.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  ))}
                </div>
              </section>

              <section className="card">
                <h3>Emotion Distribution</h3>
                <div className="emotion-distribution">
                  {statistics.emotion_distribution?.map(item => (
                    <div key={item.name} className="emotion-bar-item">
                      <span className="emotion-name">{item.name}</span>
                      <div className="emotion-bar">
                        <div 
                          className="emotion-bar-fill" 
                          style={{ 
                            width: `${Math.min((item.count / Math.max(...statistics.emotion_distribution.map(e => e.count))) * 100, 100)}%` 
                          }}
                        />
                      </div>
                      <span className="emotion-count">{item.count}</span>
                    </div>
                  ))}
                </div>
              </section>
            </div>
          </div>
        )}

        {activeTab === 'music' && (
          <div className="music-tab">
            <div className="tab-header">
              <h2>Music Recommendations</h2>
              <button className="btn-primary" onClick={handleAddMusic}>
                <Plus size={18} />
                Add Music
              </button>
            </div>
            <div className="items-table">
              <table>
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Artist</th>
                    <th>Genre</th>
                    <th>Emotion</th>
                    <th>Score</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {musicList.map(music => (
                    <tr key={music.id}>
                      <td>{music.title}</td>
                      <td>{music.artist}</td>
                      <td>{music.genre}</td>
                      <td>{music.emotion}</td>
                      <td>{music.popularity_score?.toFixed(1)}</td>
                      <td className="actions-cell">
                        <button className="icon-btn edit" onClick={() => handleEditMusic(music)}>
                          <Edit2 size={16} />
                        </button>
                        <button className="icon-btn delete" onClick={() => handleDeleteMusic(music.id)}>
                          <Trash2 size={16} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'books' && (
          <div className="books-tab">
            <div className="tab-header">
              <h2>Book Recommendations</h2>
              <button className="btn-primary" onClick={handleAddBook}>
                <Plus size={18} />
                Add Book
              </button>
            </div>
            <div className="items-table">
              <table>
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Author</th>
                    <th>Genre</th>
                    <th>Emotion</th>
                    <th>Tags</th>
                    <th>Score</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {booksList.map(book => (
                    <tr key={book.id}>
                      <td>{book.title}</td>
                      <td>{book.author}</td>
                      <td>{book.genre}</td>
                      <td>{book.emotion}</td>
                      <td>
                        <div className="tag-chips">
                          {book.tags?.slice(0, 2).map(tag => (
                            <span key={tag.id} className="tag-chip-small">{tag.name}</span>
                          ))}
                          {book.tags?.length > 2 && (
                            <span className="tag-chip-small more">+{book.tags.length - 2}</span>
                          )}
                        </div>
                      </td>
                      <td>{book.popularity_score?.toFixed(1)}</td>
                      <td className="actions-cell">
                        <button className="icon-btn edit" onClick={() => handleEditBook(book)}>
                          <Edit2 size={16} />
                        </button>
                        <button className="icon-btn delete" onClick={() => handleDeleteBook(book.id)}>
                          <Trash2 size={16} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {showMusicModal && (
        <div className="modal-overlay" onClick={() => setShowMusicModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{editingMusic ? 'Edit Music' : 'Add Music'}</h3>
              <button className="close-btn" onClick={() => setShowMusicModal(false)}>
                <X size={20} />
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Title</label>
                <input 
                  type="text" 
                  value={musicForm.title}
                  onChange={e => setMusicForm({...musicForm, title: e.target.value})}
                  placeholder="Enter title"
                />
              </div>
              <div className="form-group">
                <label>Artist</label>
                <input 
                  type="text" 
                  value={musicForm.artist}
                  onChange={e => setMusicForm({...musicForm, artist: e.target.value})}
                  placeholder="Enter artist"
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Genre</label>
                  <input 
                    type="text" 
                    value={musicForm.genre}
                    onChange={e => setMusicForm({...musicForm, genre: e.target.value})}
                    placeholder="Enter genre"
                  />
                </div>
                <div className="form-group">
                  <label>Emotion</label>
                  <select 
                    value={musicForm.emotion_id}
                    onChange={e => setMusicForm({...musicForm, emotion_id: parseInt(e.target.value)})}
                  >
                    {emotions.map(emotion => (
                      <option key={emotion.id} value={emotion.id}>
                        {emotion.emoji} {emotion.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label>YouTube URL</label>
                <input 
                  type="text" 
                  value={musicForm.youtube_url}
                  onChange={e => setMusicForm({...musicForm, youtube_url: e.target.value})}
                  placeholder="https://youtube.com/..."
                />
              </div>
              <div className="form-group">
                <label>Thumbnail URL</label>
                <input 
                  type="text" 
                  value={musicForm.thumbnail_url}
                  onChange={e => setMusicForm({...musicForm, thumbnail_url: e.target.value})}
                  placeholder="https://..."
                />
              </div>
              <div className="form-group">
                <label>Popularity Score (0-10)</label>
                <input 
                  type="number" 
                  min="0" 
                  max="10" 
                  step="0.1"
                  value={musicForm.popularity_score}
                  onChange={e => setMusicForm({...musicForm, popularity_score: parseFloat(e.target.value) || 0})}
                />
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setShowMusicModal(false)}>Cancel</button>
              <button className="btn-primary" onClick={handleSaveMusic}>
                <Save size={16} />
                Save
              </button>
            </div>
          </div>
        </div>
      )}

      {showBookModal && (
        <div className="modal-overlay" onClick={() => setShowBookModal(false)}>
          <div className="modal-content large" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{editingBook ? 'Edit Book' : 'Add Book'}</h3>
              <button className="close-btn" onClick={() => setShowBookModal(false)}>
                <X size={20} />
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Title</label>
                <input 
                  type="text" 
                  value={bookForm.title}
                  onChange={e => setBookForm({...bookForm, title: e.target.value})}
                  placeholder="Enter title"
                />
              </div>
              <div className="form-group">
                <label>Author</label>
                <input 
                  type="text" 
                  value={bookForm.author}
                  onChange={e => setBookForm({...bookForm, author: e.target.value})}
                  placeholder="Enter author"
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Genre</label>
                  <input 
                    type="text" 
                    value={bookForm.genre}
                    onChange={e => setBookForm({...bookForm, genre: e.target.value})}
                    placeholder="Enter genre"
                  />
                </div>
                <div className="form-group">
                  <label>Emotion</label>
                  <select 
                    value={bookForm.emotion_id}
                    onChange={e => setBookForm({...bookForm, emotion_id: parseInt(e.target.value)})}
                  >
                    {emotions.map(emotion => (
                      <option key={emotion.id} value={emotion.id}>
                        {emotion.emoji} {emotion.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea 
                  value={bookForm.description}
                  onChange={e => setBookForm({...bookForm, description: e.target.value})}
                  placeholder="Enter description"
                  rows={3}
                />
              </div>
              <div className="form-group">
                <label>Cover URL</label>
                <input 
                  type="text" 
                  value={bookForm.cover_url}
                  onChange={e => setBookForm({...bookForm, cover_url: e.target.value})}
                  placeholder="https://..."
                />
              </div>
              <div className="form-group">
                <label>Popularity Score (0-10)</label>
                <input 
                  type="number" 
                  min="0" 
                  max="10" 
                  step="0.1"
                  value={bookForm.popularity_score}
                  onChange={e => setBookForm({...bookForm, popularity_score: parseFloat(e.target.value) || 0})}
                />
              </div>
              <div className="form-group">
                <label>Tags</label>
                <div className="tags-select">
                  {tags.map(tag => (
                    <button 
                      key={tag.id}
                      type="button"
                      className={`tag-select-btn ${bookForm.tag_ids.includes(tag.id) ? 'selected' : ''}`}
                      onClick={() => handleTagToggle(tag.id)}
                    >
                      {tag.name}
                    </button>
                  ))}
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setShowBookModal(false)}>Cancel</button>
              <button className="btn-primary" onClick={handleSaveBook}>
                <Save size={16} />
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Admin;
