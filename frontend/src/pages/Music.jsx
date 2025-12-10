import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';
import { Music as MusicIcon, ExternalLink, ArrowLeft, Heart } from 'lucide-react';

function Music() {
  const navigate = useNavigate();
  const [musicList, setMusicList] = useState([]);
  const [emotions, setEmotions] = useState([]);
  const [selectedEmotion, setSelectedEmotion] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(function() {
    fetchEmotions();
  }, []);

  useEffect(function() {
    fetchMusic();
  }, [selectedEmotion]);

  function fetchEmotions() {
    api.get('/emotions').then(function(response) {
      setEmotions(response.data);
    }).catch(function(error) {
      console.error('Error fetching emotions:', error);
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

  function goBack() {
    navigate('/dashboard');
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

      <section className="music-section">
        <div className="music-count">
          Showing {musicList.length} tracks
        </div>
        
        {musicList.length > 0 ? (
          <div className="music-list-grid">
            {musicList.map(function(music) {
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
                    </div>
                  </div>
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
              );
            })}
          </div>
        ) : (
          <div className="empty-state">
            <MusicIcon size={48} />
            <p>No music found for this emotion</p>
          </div>
        )}
      </section>
    </div>
  );
}

export default Music;
