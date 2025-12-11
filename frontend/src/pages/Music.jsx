import { useState, useEffect, useRef } from 'react';
import api from '../api/axios';
import { Music as MusicIcon, X, Search, Heart, ExternalLink, Play } from 'lucide-react';

function getYoutubeVideoId(url) {
  if (!url) {
    return null;
  }
  var videoId = null;
  if (url.indexOf('youtube.com/watch') >= 0) {
    var parts = url.split('v=');
    if (parts.length > 1) {
      videoId = parts[1].split('&')[0];
    }
  } else if (url.indexOf('youtu.be/') >= 0) {
    var parts = url.split('youtu.be/');
    if (parts.length > 1) {
      videoId = parts[1].split('?')[0];
    }
  }
  return videoId;
}

function MusicCard(props) {
  var music = props.music;
  var isFavorite = props.isFavorite || false;
  var onToggleFavorite = props.onToggleFavorite;
  var [imgError, setImgError] = useState(false);
  
  var videoId = getYoutubeVideoId(music.youtube_url);
  var thumbnailUrl = videoId ? 'https://img.youtube.com/vi/' + videoId + '/mqdefault.jpg' : null;
  
  function handleFavoriteClick(e) {
    e.stopPropagation();
    if (onToggleFavorite) {
      onToggleFavorite(music.id);
    }
  }
  
  function handleImgError() {
    setImgError(true);
  }
  
  return (
    <div className="music-page-card">
      <div className="music-thumbnail">
        {thumbnailUrl && !imgError ? (
          <img 
            src={thumbnailUrl} 
            alt={music.title}
            onError={handleImgError}
            className="music-thumbnail-img"
          />
        ) : (
          <div className="music-page-icon"><MusicIcon size={24} /></div>
        )}
      </div>
      <div className="music-page-info">
        <div className="music-title-row">
          <h4 className="music-page-title">{music.title}</h4>
          <button 
            className={'music-favorite-btn ' + (isFavorite ? 'active' : '')} 
            onClick={handleFavoriteClick}
            title={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
          >
            <Heart size={18} fill={isFavorite ? '#ef4444' : 'none'} />
          </button>
        </div>
        <p className="music-page-artist">{music.artist}</p>
        <div className="music-page-meta">
          <span className="music-page-genre">{music.genre}</span>
          {music.emotion && (
            <span className="music-page-emotion">{music.emotion}</span>
          )}
        </div>
      </div>
      {music.youtube_url && (
        <a 
          href={music.youtube_url} 
          target="_blank" 
          rel="noopener noreferrer" 
          className="music-youtube-btn"
          onClick={function(e) { e.stopPropagation(); }}
        >
          <Play size={16} />
          YouTube
        </a>
      )}
    </div>
  );
}

function getMusicFavoritesFromStorage() {
  try {
    var stored = localStorage.getItem('music_favorites');
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (e) {
  }
  return [];
}

function saveMusicFavoritesToStorage(favoriteIds) {
  try {
    localStorage.setItem('music_favorites', JSON.stringify(favoriteIds));
  } catch (e) {
  }
}

function Music() {
  var [allMusic, setAllMusic] = useState([]);
  var [filteredMusic, setFilteredMusic] = useState([]);
  var [emotions, setEmotions] = useState([]);
  var [selectedEmotion, setSelectedEmotion] = useState('');
  var [loading, setLoading] = useState(true);
  var [favoriteIds, setFavoriteIds] = useState(getMusicFavoritesFromStorage());
  var [searchQuery, setSearchQuery] = useState('');
  var [activeTab, setActiveTab] = useState('all');
  var searchTimeoutRef = useRef(null);

  useEffect(function() {
    api.get('/music/all').then(function(res) {
      setAllMusic(res.data);
      setFilteredMusic(res.data);
      setLoading(false);
    }).catch(function() {
      setLoading(false);
    });
    
    api.get('/emotions').then(function(res) {
      setEmotions(res.data);
    });
  }, []);

  function handleEmotionFilter(emotionName) {
    if (selectedEmotion === emotionName) {
      setSelectedEmotion('');
      setFilteredMusic(allMusic);
    } else {
      setSelectedEmotion(emotionName);
      var filtered = [];
      for (var i = 0; i < allMusic.length; i++) {
        if (allMusic[i].emotion === emotionName) {
          filtered.push(allMusic[i]);
        }
      }
      setFilteredMusic(filtered);
    }
  }

  function clearEmotionFilter() {
    setSelectedEmotion('');
    setFilteredMusic(allMusic);
  }

  function handleSearch(query) {
    setSearchQuery(query);
    
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }
    
    if (!query.trim()) {
      if (selectedEmotion) {
        var emotionFiltered = [];
        for (var i = 0; i < allMusic.length; i++) {
          if (allMusic[i].emotion === selectedEmotion) {
            emotionFiltered.push(allMusic[i]);
          }
        }
        setFilteredMusic(emotionFiltered);
      } else {
        setFilteredMusic(allMusic);
      }
      return;
    }
    
    searchTimeoutRef.current = setTimeout(function() {
      var searchLower = query.toLowerCase();
      var results = [];
      var sourceList = selectedEmotion ? filteredMusic : allMusic;
      
      for (var i = 0; i < allMusic.length; i++) {
        var music = allMusic[i];
        var titleMatch = music.title.toLowerCase().indexOf(searchLower) >= 0;
        var artistMatch = music.artist.toLowerCase().indexOf(searchLower) >= 0;
        var genreMatch = music.genre && music.genre.toLowerCase().indexOf(searchLower) >= 0;
        
        if (titleMatch || artistMatch || genreMatch) {
          if (!selectedEmotion || music.emotion === selectedEmotion) {
            results.push(music);
          }
        }
      }
      setFilteredMusic(results);
    }, 300);
  }

  function clearSearch() {
    setSearchQuery('');
    if (selectedEmotion) {
      var emotionFiltered = [];
      for (var i = 0; i < allMusic.length; i++) {
        if (allMusic[i].emotion === selectedEmotion) {
          emotionFiltered.push(allMusic[i]);
        }
      }
      setFilteredMusic(emotionFiltered);
    } else {
      setFilteredMusic(allMusic);
    }
  }

  function toggleFavorite(musicId) {
    var isFav = favoriteIds.indexOf(musicId) >= 0;
    var newIds;
    
    if (isFav) {
      newIds = [];
      for (var i = 0; i < favoriteIds.length; i++) {
        if (favoriteIds[i] !== musicId) {
          newIds.push(favoriteIds[i]);
        }
      }
    } else {
      newIds = favoriteIds.concat([musicId]);
    }
    
    setFavoriteIds(newIds);
    saveMusicFavoritesToStorage(newIds);
  }

  function isFavorite(musicId) {
    return favoriteIds.indexOf(musicId) >= 0;
  }

  function handleTabChange(tab) {
    setActiveTab(tab);
    setSearchQuery('');
    setSelectedEmotion('');
    setFilteredMusic(allMusic);
  }

  function getFavoriteMusic() {
    var result = [];
    for (var i = 0; i < allMusic.length; i++) {
      var music = allMusic[i];
      if (favoriteIds.indexOf(music.id) >= 0) {
        result.push(music);
      }
    }
    return result;
  }

  function getDisplayMusic() {
    var baseList;
    if (activeTab === 'favorites') {
      baseList = getFavoriteMusic();
    } else {
      baseList = filteredMusic;
    }
    
    if (searchQuery.trim() && activeTab === 'favorites') {
      var searchLower = searchQuery.toLowerCase();
      var results = [];
      for (var i = 0; i < baseList.length; i++) {
        var music = baseList[i];
        var titleMatch = music.title.toLowerCase().indexOf(searchLower) >= 0;
        var artistMatch = music.artist.toLowerCase().indexOf(searchLower) >= 0;
        var genreMatch = music.genre && music.genre.toLowerCase().indexOf(searchLower) >= 0;
        if (titleMatch || artistMatch || genreMatch) {
          results.push(music);
        }
      }
      return results;
    }
    
    return baseList;
  }

  var displayMusic = getDisplayMusic();

  return (
    <div className="music-page">
      <header className="page-header">
        <h1><MusicIcon size={28} /> Music Recommendations</h1>
        <p>Discover music that matches your current mood</p>
      </header>

      <div className="music-search-section">
        <div className="search-input-wrapper">
          <Search size={20} className="search-icon" />
          <input
            type="text"
            className="music-search-input"
            placeholder="Search by title, artist, or genre..."
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

      <div className="music-tabs">
        <button 
          className={'music-tab ' + (activeTab === 'all' ? 'active' : '')}
          onClick={function() { handleTabChange('all'); }}
        >
          <MusicIcon size={18} />
          All Music
        </button>
        <button 
          className={'music-tab ' + (activeTab === 'favorites' ? 'active' : '')}
          onClick={function() { handleTabChange('favorites'); }}
        >
          <Heart size={18} />
          Favorites ({favoriteIds.length})
        </button>
      </div>

      {activeTab === 'all' && !searchQuery && (
        <div className="emotion-filter-section">
          <div className="emotion-filter-header">
            <span className="emotion-filter-label">Filter by Mood</span>
            {selectedEmotion && (
              <button className="clear-emotion-btn" onClick={clearEmotionFilter}>Clear</button>
            )}
          </div>
          
          <div className="emotion-chips-container">
            {emotions.map(function(emotion) {
              var isActive = selectedEmotion === emotion.name;
              return (
                <button 
                  key={emotion.id} 
                  className={'emotion-chip ' + (isActive ? 'active' : '')} 
                  onClick={function() { handleEmotionFilter(emotion.name); }}
                  style={isActive ? { backgroundColor: emotion.color, borderColor: emotion.color } : {}}
                >
                  <span>{emotion.emoji}</span>
                  {emotion.name}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {loading ? (
        <div className="loading-state">Loading music...</div>
      ) : (
        <div className="music-container">
          {displayMusic.length > 0 ? (
            <>
              <div className="music-result-info">
                {searchQuery ? (
                  displayMusic.length + ' search results for "' + searchQuery + '"'
                ) : activeTab === 'favorites' ? (
                  displayMusic.length + ' favorite songs'
                ) : selectedEmotion ? (
                  displayMusic.length + ' songs for "' + selectedEmotion + '" mood'
                ) : (
                  'All ' + displayMusic.length + ' songs'
                )}
              </div>
              <div className="music-full-grid">
                {displayMusic.map(function(music) {
                  return (
                    <MusicCard 
                      key={music.id} 
                      music={music} 
                      isFavorite={isFavorite(music.id)}
                      onToggleFavorite={toggleFavorite}
                    />
                  );
                })}
              </div>
            </>
          ) : (
            <div className="empty-state">
              <MusicIcon size={48} />
              {searchQuery ? (
                <p>No music found for "{searchQuery}"</p>
              ) : activeTab === 'favorites' ? (
                <p>No favorite songs yet. Click the heart icon to add songs to your favorites!</p>
              ) : (
                <p>No music found for selected mood.</p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default Music;
