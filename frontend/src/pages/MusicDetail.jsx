import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Heart, Play, User, Trash2, Music as MusicIcon, Check } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';

function getYouTubeVideoId(url) {
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

function saveMusicFavoritesToStorage(ids) {
  try {
    localStorage.setItem('music_favorites', JSON.stringify(ids));
  } catch (e) {
  }
}

var EMOTION_OPTIONS = [
  { name: 'Happy', emoji: '😊', color: '#fef3c7' },
  { name: 'Sad', emoji: '😢', color: '#dbeafe' },
  { name: 'Tired', emoji: '😴', color: '#e0e7ff' },
  { name: 'Angry', emoji: '😠', color: '#fee2e2' },
  { name: 'Stressed', emoji: '😰', color: '#fce7f3' },
  { name: 'Neutral', emoji: '😐', color: '#f3f4f6' }
];

function MusicDetail() {
  var { id } = useParams();
  var navigate = useNavigate();
  var { user } = useAuth();
  
  var [music, setMusic] = useState(null);
  var [allMusic, setAllMusic] = useState([]);
  var [loading, setLoading] = useState(true);
  var [error, setError] = useState('');
  var [favoriteIds, setFavoriteIds] = useState(getMusicFavoritesFromStorage());
  var [thumbnailError, setThumbnailError] = useState(false);
  
  var [reviews, setReviews] = useState([]);
  var [selectedEmotion, setSelectedEmotion] = useState('');
  var [selectedSimilarMusic, setSelectedSimilarMusic] = useState([]);
  var [reviewContent, setReviewContent] = useState('');
  var [reviewError, setReviewError] = useState('');
  var [isSubmitting, setIsSubmitting] = useState(false);
  var [hasUserReview, setHasUserReview] = useState(false);
  
  var currentUserId = user ? user.id : null;
  
  useEffect(function() {
    loadMusic();
    loadAllMusic();
  }, [id]);
  
  useEffect(function() {
    if (music) {
      loadReviews();
    }
  }, [music, currentUserId]);
  
  function loadMusic() {
    setLoading(true);
    setError('');
    
    api.get('/music/' + id).then(function(res) {
      setMusic(res.data);
      setLoading(false);
    }).catch(function() {
      setError('Music not found');
      setLoading(false);
    });
  }
  
  function loadAllMusic() {
    api.get('/music/all').then(function(res) {
      setAllMusic(res.data);
    }).catch(function() {
      setAllMusic([]);
    });
  }
  
  function loadReviews() {
    api.get('/music/' + id + '/reviews').then(function(res) {
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
  
  function isFavorite(musicId) {
    for (var i = 0; i < favoriteIds.length; i++) {
      if (favoriteIds[i] === musicId) {
        return true;
      }
    }
    return false;
  }
  
  function toggleFavorite() {
    if (!music) return;
    
    var newFavorites = [];
    var found = false;
    
    for (var i = 0; i < favoriteIds.length; i++) {
      if (favoriteIds[i] === music.id) {
        found = true;
      } else {
        newFavorites.push(favoriteIds[i]);
      }
    }
    
    if (!found) {
      newFavorites.push(music.id);
    }
    
    setFavoriteIds(newFavorites);
    saveMusicFavoritesToStorage(newFavorites);
  }
  
  function handleBack() {
    navigate('/music');
  }
  
  function handleEmotionSelect(emotionName) {
    setSelectedEmotion(emotionName);
  }
  
  function isSimilarSelected(musicId) {
    for (var i = 0; i < selectedSimilarMusic.length; i++) {
      if (selectedSimilarMusic[i] === musicId) {
        return true;
      }
    }
    return false;
  }
  
  function handleSimilarMusicToggle(musicId) {
    if (isSimilarSelected(musicId)) {
      var newSelected = [];
      for (var i = 0; i < selectedSimilarMusic.length; i++) {
        if (selectedSimilarMusic[i] !== musicId) {
          newSelected.push(selectedSimilarMusic[i]);
        }
      }
      setSelectedSimilarMusic(newSelected);
    } else {
      if (selectedSimilarMusic.length < 3) {
        var newSelected = selectedSimilarMusic.slice();
        newSelected.push(musicId);
        setSelectedSimilarMusic(newSelected);
      }
    }
  }
  
  function handleSubmitReview() {
    if (!selectedEmotion) {
      setReviewError('Please select how you felt');
      return;
    }
    if (!reviewContent.trim()) {
      setReviewError('Please write a review');
      return;
    }
    
    setIsSubmitting(true);
    setReviewError('');
    
    api.post('/music/' + id + '/reviews', {
      emotion: selectedEmotion,
      content: reviewContent.trim(),
      similar_music_ids: selectedSimilarMusic
    }).then(function() {
      setReviewContent('');
      setSelectedEmotion('');
      setSelectedSimilarMusic([]);
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
  
  function getEmotionInfo(emotionName) {
    for (var i = 0; i < EMOTION_OPTIONS.length; i++) {
      if (EMOTION_OPTIONS[i].name === emotionName) {
        return EMOTION_OPTIONS[i];
      }
    }
    return { name: emotionName, emoji: '🎵', color: '#f3f4f6' };
  }
  
  function getOtherMusic() {
    var others = [];
    for (var i = 0; i < allMusic.length; i++) {
      if (Number(allMusic[i].id) !== Number(id)) {
        others.push(allMusic[i]);
      }
    }
    return others;
  }
  
  function getMusicById(musicId) {
    for (var i = 0; i < allMusic.length; i++) {
      if (Number(allMusic[i].id) === Number(musicId)) {
        return allMusic[i];
      }
    }
    return null;
  }
  
  var thumbnailUrl = null;
  if (music && music.youtube_url) {
    var videoId = getYouTubeVideoId(music.youtube_url);
    if (videoId) {
      thumbnailUrl = 'https://img.youtube.com/vi/' + videoId + '/mqdefault.jpg';
    }
  }
  
  if (loading) {
    return (
      <div className="music-detail-page">
        <div className="loading-state">Loading music...</div>
      </div>
    );
  }
  
  if (error || !music) {
    return (
      <div className="music-detail-page">
        <div className="error-state">
          <p>{error || 'Music not found'}</p>
          <button className="back-btn" onClick={handleBack}>
            <ArrowLeft size={20} />
            Back to Music
          </button>
        </div>
      </div>
    );
  }
  
  var otherMusic = getOtherMusic();
  
  return (
    <div className="music-detail-page">
      <button className="back-btn" onClick={handleBack}>
        <ArrowLeft size={20} />
        Back to Music
      </button>
      
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
            <div className="music-detail-icon"><MusicIcon size={64} /></div>
          )}
        </div>
        <div className="music-detail-info">
          <h1>{music.title}</h1>
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
          onClick={toggleFavorite}
        >
          <Heart size={20} fill={isFavorite(music.id) ? '#ef4444' : 'none'} />
          {isFavorite(music.id) ? 'Remove from Favorites' : 'Add to Favorites'}
        </button>
        {music.youtube_url && (
          <a 
            href={music.youtube_url} 
            target="_blank" 
            rel="noopener noreferrer" 
            className="youtube-btn-large"
          >
            <Play size={20} />
            Watch on YouTube
          </a>
        )}
      </div>
      
      <div className="music-detail-reviews">
        <h3>Reviews ({reviews.length})</h3>
        
        {!hasUserReview && (
          <div className="review-form">
            <div className="emotion-select-section">
              <label>How did you feel listening to this music?</label>
              <div className="emotion-tags">
                {EMOTION_OPTIONS.map(function(emotion) {
                  return (
                    <button
                      key={emotion.name}
                      type="button"
                      className={'emotion-tag-btn ' + (selectedEmotion === emotion.name ? 'selected' : '')}
                      style={{ backgroundColor: selectedEmotion === emotion.name ? emotion.color : undefined }}
                      onClick={function() { handleEmotionSelect(emotion.name); }}
                    >
                      <span>{emotion.emoji}</span>
                      {emotion.name}
                    </button>
                  );
                })}
              </div>
            </div>
            
            <div className="similar-music-section">
              <label>Select up to 3 similar music ({selectedSimilarMusic.length}/3)</label>
              <div className="similar-music-grid">
                {otherMusic.map(function(m) {
                  var isSelected = isSimilarSelected(m.id);
                  return (
                    <button
                      key={m.id}
                      type="button"
                      className={'similar-music-item ' + (isSelected ? 'selected' : '')}
                      onClick={function() { handleSimilarMusicToggle(m.id); }}
                      disabled={!isSelected && selectedSimilarMusic.length >= 3}
                    >
                      {isSelected && <Check size={16} className="check-icon" />}
                      <span className="similar-music-title">{m.title}</span>
                      <span className="similar-music-artist">{m.artist}</span>
                    </button>
                  );
                })}
              </div>
            </div>
            
            <textarea
              className="review-textarea"
              placeholder="Write your thoughts about this music..."
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
              var emotionInfo = getEmotionInfo(review.emotion);
              return (
                <div key={review.id} className="review-item">
                  <div className="review-header">
                    <span className="review-user">
                      <User size={16} />
                      {review.username}
                    </span>
                    <span 
                      className="review-emotion-tag"
                      style={{ backgroundColor: emotionInfo.color }}
                    >
                      {emotionInfo.emoji} {emotionInfo.name}
                    </span>
                    {Number(review.user_id) === Number(currentUserId) && (
                      <button 
                        className="review-delete-btn"
                        onClick={function() { handleDeleteReview(review.id); }}
                      >
                        <Trash2 size={16} />
                      </button>
                    )}
                  </div>
                  <p className="review-content">{review.content}</p>
                  {review.similar_music_ids && review.similar_music_ids.length > 0 && (
                    <div className="review-similar-music">
                      <span className="similar-label">Similar music:</span>
                      {review.similar_music_ids.map(function(similarId) {
                        var similarMusic = getMusicById(similarId);
                        if (similarMusic) {
                          return (
                            <span key={similarId} className="similar-music-chip">
                              {similarMusic.title}
                            </span>
                          );
                        }
                        return null;
                      })}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}

export default MusicDetail;
