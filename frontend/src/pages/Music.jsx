import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';
import { Music as MusicIcon, ExternalLink, ArrowLeft, Heart, Sparkles } from 'lucide-react';

function Music() {
  const navigate = useNavigate();
  const [musicList, setMusicList] = useState([]);
  const [emotions, setEmotions] = useState([]);
  const [selectedEmotion, setSelectedEmotion] = useState('all');
  const [favoriteIds, setFavoriteIds] = useState(new Set());
  const [similarMusic, setSimilarMusic] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('all');

  useEffect(function() {
    fetchEmotions();
    fetchFavoriteIds();
    fetchSimilarMusic();
  }, []);

  useEffect(function() {
    if (activeTab === 'all') {
      fetchMusic();
    } else if (activeTab === 'favorites') {
      fetchFavorites();
    }
  }, [selectedEmotion, activeTab]);

  function fetchEmotions() {
    api.get('/emotions').then(function(response) {
      setEmotions(response.data);
    }).catch(function(error) {
      console.error('Error fetching emotions:', error);
    });
  }

  function fetchFavoriteIds() {
    api.get('/music/favorites/ids').then(function(response) {
      setFavoriteIds(new Set(response.data));
    }).catch(function(error) {
      console.error('Error fetching favorite ids:', error);
    });
  }

  function fetchFavorites() {
    setLoading(true);
    api.get('/music/favorites').then(function(response) {
      setMusicList(response.data);
      setLoading(false);
    }).catch(function(error) {
      console.error('Error fetching favorites:', error);
      setLoading(false);
    });
  }

  function fetchSimilarMusic() {
    api.get('/music/similar', { params: { limit: 6 } }).then(function(response) {
      setSimilarMusic(response.data);
    }).catch(function(error) {
      console.error('Error fetching similar music:', error);
    });
  }

  function fetchMusic() {
    setLoading(true);
    
    var url = '';
    var params = {};
    
    if (selectedEmotion === 'all') {
      url = '/music/all';
    } else {
      url = '/music/recommendations';
      params.emotion = selectedEmotion;
      params.limit = 100;
    }
    
    api.get(url, { params: params }).then(function(response) {
      setMusicList(response.data);
      setLoading(false);
    }).catch(function(error) {
      console.error('Error fetching music:', error);
      setLoading(false);
    });
  }

  function handleEmotionFilter(emotionName) {
    setSelectedEmotion(emotionName);
  }

  function toggleFavorite(musicId) {
    var isFavorited = favoriteIds.has(musicId);
    
    if (isFavorited) {
      api.delete('/music/favorites/' + musicId).then(function() {
        var newSet = new Set(favoriteIds);
        newSet.delete(musicId);
        setFavoriteIds(newSet);
        fetchSimilarMusic();
        if (activeTab === 'favorites') {
          fetchFavorites();
        }
      }).catch(function(error) {
        console.error('Error removing favorite:', error);
      });
    } else {
      api.post('/music/favorites/' + musicId).then(function() {
        var newSet = new Set(favoriteIds);
        newSet.add(musicId);
        setFavoriteIds(newSet);
        fetchSimilarMusic();
      }).catch(function(error) {
        console.error('Error adding favorite:', error);
      });
    }
  }

  function goBack() {
    navigate('/dashboard');
  }

  function renderMusicCard(music, showScore) {
    var isFavorited = favoriteIds.has(music.id);
    
    return (
      <div key={music.id} className="music-list-card">
        <div className="music-list-icon">
          <MusicIcon size={32} />
        </div>
        <div className="music-list-info">
          <h4 className="music-list-title">{music.title}</h4>
          <p className="music-list-artist">{music.artist}</p>
          <div className="music-list-meta">
            <span className="music-genre-tag">{music.genre}</span>
            <span className="music-emotion-tag">{music.emotion}</span>
            {showScore && music.similarity_score && (
              <span className="music-score-tag">Match: {music.similarity_score}</span>
            )}
          </div>
        </div>
        <div className="music-card-actions">
          <button 
            className={'favorite-btn ' + (isFavorited ? 'active' : '')}
            onClick={function() { toggleFavorite(music.id); }}
          >
            <Heart size={20} fill={isFavorited ? '#ef4444' : 'none'} />
          </button>
          {music.youtube_url && (
            <a 
              href={music.youtube_url} 
              target="_blank" 
              rel="noopener noreferrer" 
              className="music-play-btn"
            >
              <ExternalLink size={18} />
              Play
            </a>
          )}
        </div>
      </div>
    );
  }

  if (loading) {
    return <div className="loading-screen">Loading...</div>;
  }

  return (
    <div className="music-page">
      <header className="page-header">
        <button className="back-btn" onClick={goBack}>
          <ArrowLeft size={20} />
          Back to Dashboard
        </button>
        <h1><MusicIcon size={28} /> Music Recommendations</h1>
        <p className="page-subtitle">Discover music that matches your mood</p>
      </header>

      <div className="music-tabs">
        <button 
          className={'tab-btn ' + (activeTab === 'all' ? 'active' : '')}
          onClick={function() { setActiveTab('all'); }}
        >
          All Music
        </button>
        <button 
          className={'tab-btn ' + (activeTab === 'favorites' ? 'active' : '')}
          onClick={function() { setActiveTab('favorites'); }}
        >
          <Heart size={16} /> Favorites ({favoriteIds.size})
        </button>
      </div>

      {similarMusic.length > 0 && (
        <section className="similar-section card">
          <div className="section-header">
            <h3><Sparkles size={20} /> Recommended for You</h3>
            <p className="section-hint">Based on your favorites</p>
          </div>
          <div className="similar-music-grid">
            {similarMusic.map(function(music) {
              return renderMusicCard(music, true);
            })}
          </div>
        </section>
      )}

      {activeTab === 'all' && (
        <section className="filter-section">
          <h3>Filter by Emotion</h3>
          <div className="emotion-filters">
            <button 
              className={'filter-btn ' + (selectedEmotion === 'all' ? 'active' : '')}
              onClick={function() { handleEmotionFilter('all'); }}
            >
              All
            </button>
            {emotions.map(function(emotion) {
              return (
                <button
                  key={emotion.id}
                  className={'filter-btn ' + (selectedEmotion === emotion.name ? 'active' : '')}
                  onClick={function() { handleEmotionFilter(emotion.name); }}
                >
                  {emotion.emoji} {emotion.name}
                </button>
              );
            })}
          </div>
        </section>
      )}

      <section className="music-section">
        <div className="music-count">
          {activeTab === 'all' ? 'Showing ' + musicList.length + ' tracks' : 'Your favorites: ' + musicList.length + ' tracks'}
        </div>
        
        {musicList.length > 0 ? (
          <div className="music-list-grid">
            {musicList.map(function(music) {
              return renderMusicCard(music, false);
            })}
          </div>
        ) : (
          <div className="empty-state">
            <MusicIcon size={48} />
            <p>{activeTab === 'favorites' ? 'No favorites yet. Click the heart icon to add!' : 'No music found for this emotion'}</p>
          </div>
        )}
      </section>
    </div>
  );
}

export default Music;
