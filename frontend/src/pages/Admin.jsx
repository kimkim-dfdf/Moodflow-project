import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Navigate } from 'react-router-dom';
import api from '../api/axios';
import { 
  BarChart3, Users, Music, BookOpen, Plus, Trash2, Edit2, X, Save,
  CheckCircle2, Clock, TrendingUp
} from 'lucide-react';

function Admin() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('stats');
  const [stats, setStats] = useState(null);
  const [music, setMusic] = useState([]);
  const [books, setBooks] = useState([]);
  const [tags, setTags] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showMusicModal, setShowMusicModal] = useState(false);
  const [showBookModal, setShowBookModal] = useState(false);
  const [editingMusic, setEditingMusic] = useState(null);
  const [editingBook, setEditingBook] = useState(null);

  const emotions = ['Happy', 'Sad', 'Tired', 'Angry', 'Stressed', 'Neutral'];

  useEffect(function() {
    if (user && user.is_admin) {
      fetchData();
    }
  }, [user]);

  function fetchData() {
    setLoading(true);
    Promise.all([
      api.get('/admin/stats'),
      api.get('/admin/music'),
      api.get('/admin/books'),
      api.get('/admin/tags')
    ]).then(function(results) {
      setStats(results[0].data);
      setMusic(results[1].data);
      setBooks(results[2].data);
      setTags(results[3].data);
      setLoading(false);
    }).catch(function() {
      setLoading(false);
    });
  }

  function handleSaveMusic(data) {
    if (editingMusic && editingMusic.is_custom) {
      api.put('/admin/music/' + editingMusic.id, data).then(function() {
        fetchData();
        setShowMusicModal(false);
        setEditingMusic(null);
      });
    } else {
      api.post('/admin/music', data).then(function() {
        fetchData();
        setShowMusicModal(false);
      });
    }
  }

  function handleDeleteMusic(id) {
    if (confirm('Are you sure you want to delete this music?')) {
      api.delete('/admin/music/' + id).then(fetchData);
    }
  }

  function handleSaveBook(data) {
    if (editingBook && editingBook.is_custom) {
      api.put('/admin/books/' + editingBook.id, data).then(function() {
        fetchData();
        setShowBookModal(false);
        setEditingBook(null);
      });
    } else {
      api.post('/admin/books', data).then(function() {
        fetchData();
        setShowBookModal(false);
      });
    }
  }

  function handleDeleteBook(id) {
    if (confirm('Are you sure you want to delete this book?')) {
      api.delete('/admin/books/' + id).then(fetchData);
    }
  }

  if (!user || !user.is_admin) {
    return <Navigate to="/dashboard" />;
  }

  if (loading) {
    return <div className="loading-screen">Loading...</div>;
  }

  return (
    <div className="admin-page">
      <header className="page-header">
        <h1><BarChart3 size={28} /> Admin Dashboard</h1>
        <p>Manage content and view statistics</p>
      </header>

      <div className="admin-tabs">
        <button 
          className={activeTab === 'stats' ? 'tab-btn active' : 'tab-btn'}
          onClick={function() { setActiveTab('stats'); }}
        >
          <TrendingUp size={18} /> Statistics
        </button>
        <button 
          className={activeTab === 'music' ? 'tab-btn active' : 'tab-btn'}
          onClick={function() { setActiveTab('music'); }}
        >
          <Music size={18} /> Music
        </button>
        <button 
          className={activeTab === 'books' ? 'tab-btn active' : 'tab-btn'}
          onClick={function() { setActiveTab('books'); }}
        >
          <BookOpen size={18} /> Books
        </button>
      </div>

      {activeTab === 'stats' && stats && (
        <div className="stats-section">
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon users"><Users size={24} /></div>
              <div className="stat-info">
                <span className="stat-value">{stats.total_users}</span>
                <span className="stat-label">Total Users</span>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon tasks"><CheckCircle2 size={24} /></div>
              <div className="stat-info">
                <span className="stat-value">{stats.tasks.total}</span>
                <span className="stat-label">Total Tasks</span>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon completed"><CheckCircle2 size={24} /></div>
              <div className="stat-info">
                <span className="stat-value">{stats.tasks.completed}</span>
                <span className="stat-label">Completed Tasks</span>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon pending"><Clock size={24} /></div>
              <div className="stat-info">
                <span className="stat-value">{stats.tasks.pending}</span>
                <span className="stat-label">Pending Tasks</span>
              </div>
            </div>
          </div>

          <div className="stats-details">
            <div className="detail-card">
              <h3><Users size={20} /> User Activity</h3>
              <div className="user-stats-list">
                {stats.users.map(function(u) {
                  return (
                    <div key={u.user_id} className="user-stat-row">
                      <div className="user-info">
                        <span className="user-name">{u.username}</span>
                        <span className="user-email">{u.email}</span>
                      </div>
                      <div className="user-metrics">
                        <span className="metric">
                          <CheckCircle2 size={14} /> {u.completed_tasks}/{u.total_tasks} tasks
                        </span>
                        <span className="metric">
                          {u.emotion_entries} mood entries
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="detail-card">
              <h3>Emotion Distribution</h3>
              <div className="emotion-stats-list">
                {stats.emotions.map(function(e) {
                  return (
                    <div key={e.emotion.id} className="emotion-stat-row">
                      <span className="emotion-emoji">{e.emotion.emoji}</span>
                      <span className="emotion-name">{e.emotion.name}</span>
                      <div className="emotion-bar-container">
                        <div 
                          className="emotion-bar" 
                          style={{ 
                            width: Math.min(e.count * 20, 100) + '%',
                            backgroundColor: e.emotion.color 
                          }}
                        ></div>
                      </div>
                      <span className="emotion-count">{e.count}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="detail-card">
              <h3>Tasks by Category</h3>
              <div className="category-stats-list">
                {Object.entries(stats.tasks.by_category || {}).map(function(entry) {
                  var category = entry[0];
                  var count = entry[1];
                  return (
                    <div key={category} className="category-stat-row">
                      <span className="category-name">{category}</span>
                      <span className="category-count">{count}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'music' && (
        <div className="content-section">
          <div className="section-header">
            <h3>Music Recommendations ({music.length})</h3>
            <button className="add-btn" onClick={function() { setEditingMusic(null); setShowMusicModal(true); }}>
              <Plus size={18} /> Add Music
            </button>
          </div>
          <div className="content-table">
            <table>
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Artist</th>
                  <th>Genre</th>
                  <th>Emotion</th>
                  <th>Type</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {music.map(function(m) {
                  return (
                    <tr key={m.id}>
                      <td>{m.title}</td>
                      <td>{m.artist}</td>
                      <td>{m.genre}</td>
                      <td><span className="emotion-badge">{m.emotion}</span></td>
                      <td>
                        <span className={m.is_custom ? 'type-badge custom' : 'type-badge static'}>
                          {m.is_custom ? 'Custom' : 'Static'}
                        </span>
                      </td>
                      <td>
                        {m.is_custom && (
                          <div className="action-btns">
                            <button className="edit-btn" onClick={function() { setEditingMusic(m); setShowMusicModal(true); }}>
                              <Edit2 size={16} />
                            </button>
                            <button className="delete-btn" onClick={function() { handleDeleteMusic(m.id); }}>
                              <Trash2 size={16} />
                            </button>
                          </div>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'books' && (
        <div className="content-section">
          <div className="section-header">
            <h3>Book Recommendations ({books.length})</h3>
            <button className="add-btn" onClick={function() { setEditingBook(null); setShowBookModal(true); }}>
              <Plus size={18} /> Add Book
            </button>
          </div>
          <div className="content-table">
            <table>
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Author</th>
                  <th>Genre</th>
                  <th>Emotion</th>
                  <th>Tags</th>
                  <th>Type</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {books.map(function(b) {
                  return (
                    <tr key={b.id}>
                      <td>{b.title}</td>
                      <td>{b.author}</td>
                      <td>{b.genre}</td>
                      <td><span className="emotion-badge">{b.emotion}</span></td>
                      <td>
                        <div className="tag-list">
                          {(b.tags || []).slice(0, 2).map(function(t) {
                            return <span key={t} className="tag-mini">{t}</span>;
                          })}
                          {(b.tags || []).length > 2 && <span className="tag-more">+{b.tags.length - 2}</span>}
                        </div>
                      </td>
                      <td>
                        <span className={b.is_custom ? 'type-badge custom' : 'type-badge static'}>
                          {b.is_custom ? 'Custom' : 'Static'}
                        </span>
                      </td>
                      <td>
                        {b.is_custom && (
                          <div className="action-btns">
                            <button className="edit-btn" onClick={function() { setEditingBook(b); setShowBookModal(true); }}>
                              <Edit2 size={16} />
                            </button>
                            <button className="delete-btn" onClick={function() { handleDeleteBook(b.id); }}>
                              <Trash2 size={16} />
                            </button>
                          </div>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {showMusicModal && (
        <MusicModal
          music={editingMusic}
          emotions={emotions}
          onSave={handleSaveMusic}
          onClose={function() { setShowMusicModal(false); setEditingMusic(null); }}
        />
      )}

      {showBookModal && (
        <BookModal
          book={editingBook}
          emotions={emotions}
          tags={tags}
          onSave={handleSaveBook}
          onClose={function() { setShowBookModal(false); setEditingBook(null); }}
        />
      )}
    </div>
  );
}

function MusicModal({ music, emotions, onSave, onClose }) {
  const [form, setForm] = useState({
    title: music ? music.title : '',
    artist: music ? music.artist : '',
    genre: music ? music.genre : '',
    emotion: music ? music.emotion : 'Happy',
    youtube_url: music ? music.youtube_url : ''
  });

  function handleSubmit(e) {
    e.preventDefault();
    onSave(form);
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={function(e) { e.stopPropagation(); }}>
        <div className="modal-header">
          <h3>{music ? 'Edit Music' : 'Add Music'}</h3>
          <button className="close-btn" onClick={onClose}><X size={20} /></button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Title *</label>
            <input 
              type="text" 
              value={form.title} 
              onChange={function(e) { setForm({...form, title: e.target.value}); }}
              required
            />
          </div>
          <div className="form-group">
            <label>Artist</label>
            <input 
              type="text" 
              value={form.artist} 
              onChange={function(e) { setForm({...form, artist: e.target.value}); }}
            />
          </div>
          <div className="form-group">
            <label>Genre</label>
            <input 
              type="text" 
              value={form.genre} 
              onChange={function(e) { setForm({...form, genre: e.target.value}); }}
            />
          </div>
          <div className="form-group">
            <label>Emotion *</label>
            <select 
              value={form.emotion} 
              onChange={function(e) { setForm({...form, emotion: e.target.value}); }}
            >
              {emotions.map(function(em) {
                return <option key={em} value={em}>{em}</option>;
              })}
            </select>
          </div>
          <div className="form-group">
            <label>YouTube URL</label>
            <input 
              type="text" 
              value={form.youtube_url} 
              onChange={function(e) { setForm({...form, youtube_url: e.target.value}); }}
              placeholder="https://www.youtube.com/watch?v=..."
            />
          </div>
          <div className="modal-actions">
            <button type="button" className="cancel-btn" onClick={onClose}>Cancel</button>
            <button type="submit" className="save-btn"><Save size={16} /> Save</button>
          </div>
        </form>
      </div>
    </div>
  );
}

function BookModal({ book, emotions, tags, onSave, onClose }) {
  const [form, setForm] = useState({
    title: book ? book.title : '',
    author: book ? book.author : '',
    genre: book ? book.genre : '',
    emotion: book ? book.emotion : 'Happy',
    description: book ? book.description : '',
    tags: book ? book.tags : []
  });

  function handleSubmit(e) {
    e.preventDefault();
    onSave(form);
  }

  function toggleTag(slug) {
    if (form.tags.indexOf(slug) >= 0) {
      setForm({...form, tags: form.tags.filter(function(t) { return t !== slug; })});
    } else {
      setForm({...form, tags: form.tags.concat([slug])});
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content book-modal" onClick={function(e) { e.stopPropagation(); }}>
        <div className="modal-header">
          <h3>{book ? 'Edit Book' : 'Add Book'}</h3>
          <button className="close-btn" onClick={onClose}><X size={20} /></button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label>Title *</label>
              <input 
                type="text" 
                value={form.title} 
                onChange={function(e) { setForm({...form, title: e.target.value}); }}
                required
              />
            </div>
            <div className="form-group">
              <label>Author</label>
              <input 
                type="text" 
                value={form.author} 
                onChange={function(e) { setForm({...form, author: e.target.value}); }}
              />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Genre</label>
              <input 
                type="text" 
                value={form.genre} 
                onChange={function(e) { setForm({...form, genre: e.target.value}); }}
              />
            </div>
            <div className="form-group">
              <label>Emotion</label>
              <select 
                value={form.emotion} 
                onChange={function(e) { setForm({...form, emotion: e.target.value}); }}
              >
                {emotions.map(function(em) {
                  return <option key={em} value={em}>{em}</option>;
                })}
              </select>
            </div>
          </div>
          <div className="form-group">
            <label>Description</label>
            <textarea 
              value={form.description} 
              onChange={function(e) { setForm({...form, description: e.target.value}); }}
              rows={3}
            />
          </div>
          <div className="form-group">
            <label>Tags</label>
            <div className="tag-selector">
              {tags.map(function(tag) {
                var isSelected = form.tags.indexOf(tag.slug) >= 0;
                return (
                  <button 
                    type="button"
                    key={tag.slug} 
                    className={isSelected ? 'tag-chip selected' : 'tag-chip'}
                    style={isSelected ? { backgroundColor: tag.color, borderColor: tag.color } : {}}
                    onClick={function() { toggleTag(tag.slug); }}
                  >
                    {tag.name}
                  </button>
                );
              })}
            </div>
          </div>
          <div className="modal-actions">
            <button type="button" className="cancel-btn" onClick={onClose}>Cancel</button>
            <button type="submit" className="save-btn"><Save size={16} /> Save</button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default Admin;
