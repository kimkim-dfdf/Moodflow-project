import { useState, useEffect, useRef } from 'react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { Music as MusicIcon, Search, Heart, Play, X, User, Trash2, Tag } from 'lucide-react';

function getYoutubeVideoId(url) {
  if (!url) {
    return null;
  }
  var videoId = null;
  if (url.indexOf('youtu.be/') !== -1) {
    var parts = url.split('youtu.be/');
    if (parts.length > 1) {
      var idPart = parts[1].split('?')[0];
      videoId = idPart.split('&')[0];
    }
  } else if (url.indexOf('youtube.com/watch') !== -1) {
    var queryString = url.split('?')[1];
    if (queryString) {
      var params = queryString.split('&');
      for (var i = 0; i < params.length; i++) {
        if (params[i].indexOf('v=') === 0) {
          videoId = params[i].substring(2);
          break;
        }
      }
    }
  }
  return videoId;
}

function MusicCard(props) {
  var music = props.music;
  var isFavorite = props.isFavorite || false;
  var onToggleFavorite = props.onToggleFavorite;
  var onSelect = props.onSelect;
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
  
  function handleCardClick() {
    if (onSelect) {
      onSelect(music);
    }
  }
  
  return (
    <div 
      className="music-page-card"
      onClick={handleCardClick} 
      style={{cursor: 'pointer'}}
    >
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

function MusicDetailView(props) {
  var music = props.music;
  var favoriteIds = props.favoriteIds;
  var onToggleFavorite = props.onToggleFavorite;
  
  var { user } = useAuth();
  var currentUserId = user ? user.id : null;
  
  var [thumbnailError, setThumbnailError] = useState(false);
  var [reviews, setReviews] = useState([]);
  var [reviewContent, setReviewContent] = useState('');
  var [reviewError, setReviewError] = useState('');
  var [isSubmitting, setIsSubmitting] = useState(false);
  var [hasUserReview, setHasUserReview] = useState(false);
  var [listeningTags, setListeningTags] = useState([]);
  
  useEffect(function() {
    if (music) {
      setThumbnailError(false);
      setReviewContent('');
      setReviewError('');
      loadReviews();
      loadTags();
    }
  }, [music, currentUserId]);
  
  function loadReviews() {
    api.get('/music/' + music.id + '/reviews').then(function(res) {
      setReviews(res.data);
      var userHasReview = false;
      for (var i = 0; i < res.data.length; i++) {
        if (Number(res.data[i].user_id) === Number(currentUserId)) {
          userHasReview = true;
          break;
        }
      }
      setHasUserReview(userHasReview);
    }).catch(function() {
      setReviews([]);
    });
  }
  
  function loadTags() {
    api.get('/music/' + music.id + '/tags').then(function(res) {
      setListeningTags(res.data);
    }).catch(function() {
      setListeningTags([]);
    });
  }
  
  function isFavorite(musicId) {
    for (var i = 0; i < favoriteIds.length; i++) {
      if (favoriteIds[i] === musicId) {
        return true;
      }
    }
    return false;
  }
  
  function handleTagClick(tag) {
    if (tag.user_tagged) {
      api.delete('/music/' + music.id + '/tags/' + tag.id).then(function() {
        loadTags();
      }).catch(function() {});
    } else {
      api.post('/music/' + music.id + '/tags/' + tag.id).then(function() {
        loadTags();
      }).catch(function() {});
    }
  }
  
  function handleSubmitReview() {
    if (!reviewContent.trim()) {
      setReviewError('Please write a review');
      return;
    }
    
    setIsSubmitting(true);
    setReviewError('');
    
    api.post('/music/' + music.id + '/reviews', {
      content: reviewContent.trim()
    }).then(function() {
      setReviewContent('');
      loadReviews();
      setIsSubmitting(false);
    }).catch(function(err) {
      setReviewError(err.response?.data?.error || 'Failed to submit review');
      setIsSubmitting(false);
    });
  }
  
  function handleDeleteReview(reviewId) {
    api.delete('/music/reviews/' + reviewId).then(function() {
      loadReviews();
    }).catch(function() {
    });
  }
  
  var thumbnailUrl = null;
  if (music && music.youtube_url) {
    var videoId = getYoutubeVideoId(music.youtube_url);
    if (videoId) {
      thumbnailUrl = 'https://img.youtube.com/vi/' + videoId + '/mqdefault.jpg';
    }
  }
  
  return (
    <div className="music-detail-inline">
      <div className="music-detail-header">
        <div className="music-detail-thumbnail">
          {thumbnailUrl && !thumbnailError ? (
            <img 
              src={thumbnailUrl} 
              alt={music.title}
              onError={function() { setThumbnailError(true); }}
              className="music-detail-thumbnail-img"
            />
          ) : (
            <div className="music-detail-icon"><MusicIcon size={48} /></div>
          )}
        </div>
        <div className="music-detail-info">
          <h2>{music.title}</h2>
          <p className="music-detail-artist">{music.artist}</p>
          <div className="music-detail-meta">
            <span className="music-detail-genre">{music.genre}</span>
            {music.emotion && (
              <span className="music-detail-emotion">Mood: {music.emotion}</span>
            )}
          </div>
        </div>
      </div>
      
      <div className="music-detail-actions">
        <button 
          className={'favorite-btn-large ' + (isFavorite(music.id) ? 'active' : '')}
          onClick={function() { onToggleFavorite(music.id); }}
        >
          <Heart size={18} fill={isFavorite(music.id) ? '#ef4444' : 'none'} />
          {isFavorite(music.id) ? 'Remove from Favorites' : 'Add to Favorites'}
        </button>
        {music.youtube_url && (
          <a 
            href={music.youtube_url} 
            target="_blank" 
            rel="noopener noreferrer" 
            className="youtube-btn-large"
          >
            <Play size={18} />
            Watch on YouTube
          </a>
        )}
      </div>
      
      <div className="music-listening-tags">
        <h4><Tag size={16} /> Listening Tags</h4>
        <p className="listening-tags-hint">Click tags to describe when you listen to this music</p>
        <div className="listening-tags-list">
          {listeningTags.map(function(tag) {
            return (
              <button 
                key={tag.id}
                className={'listening-tag-btn ' + (tag.user_tagged ? 'active' : '')}
                onClick={function() { handleTagClick(tag); }}
              >
                {tag.name}
                {tag.count > 0 && <span className="tag-count">{tag.count}</span>}
              </button>
            );
          })}
        </div>
      </div>
      
      <div className="music-detail-reviews">
        <h4>Reviews ({reviews.length})</h4>
        
        {!hasUserReview && (
          <div className="review-form">
            <textarea
              className="review-textarea"
              placeholder="Write your review..."
              value={reviewContent}
              onChange={function(e) { setReviewContent(e.target.value); }}
              rows={3}
            />
            {reviewError && <div className="review-error">{reviewError}</div>}
            <button 
              className="review-submit-btn"
              onClick={handleSubmitReview}
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Submitting...' : 'Submit Review'}
            </button>
          </div>
        )}
        
        {hasUserReview && (
          <div className="review-notice">You have already reviewed this music.</div>
        )}
        
        <div className="reviews-list">
          {reviews.length === 0 ? (
            <p className="no-reviews">No reviews yet. Be the first to review!</p>
          ) : (
            reviews.map(function(review) {
              return (
                <div key={review.id} className="review-item">
                  <div className="review-header">
                    <span className="review-user">
                      <User size={14} />
                      {review.username}
                    </span>
                    {Number(review.user_id) === Number(currentUserId) && (
                      <button 
                        className="review-delete-btn"
                        onClick={function() { handleDeleteReview(review.id); }}
                      >
                        <Trash2 size={14} />
                      </button>
                    )}
                  </div>
                  {review.listening_tags && review.listening_tags.length > 0 && (
                    <div className="review-tags">
                      {review.listening_tags.map(function(tagName, idx) {
                        return <span key={idx} className="review-tag">{tagName}</span>;
                      })}
                    </div>
                  )}
                  <p className="review-content">{review.content}</p>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
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
  var [selectedMusic, setSelectedMusic] = useState(null);
  var searchTimeoutRef = useRef(null);
  
  function selectMusic(music) {
    setSelectedMusic(music);
  }
  
  function backToList() {
    setSelectedMusic(null);
  }

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
    setSelectedMusic(null);
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

      {activeTab === 'all' && !searchQuery && !selectedMusic && (
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

      {selectedMusic ? (
        <MusicDetailView 
          music={selectedMusic}
          onBack={backToList}
          favoriteIds={favoriteIds}
          onToggleFavorite={toggleFavorite}
        />
      ) : (
        loading ? (
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
                        onSelect={selectMusic}
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
        )
      )}
    </div>
  );
}

export default Music;
