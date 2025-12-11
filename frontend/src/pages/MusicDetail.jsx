import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Heart, Play, Star, User, Trash2, Music as MusicIcon } from 'lucide-react';
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

function MusicDetail() {
  var { id } = useParams();
  var navigate = useNavigate();
  var { user } = useAuth();
  
  var [music, setMusic] = useState(null);
  var [loading, setLoading] = useState(true);
  var [error, setError] = useState('');
  var [favoriteIds, setFavoriteIds] = useState(getMusicFavoritesFromStorage());
  var [thumbnailError, setThumbnailError] = useState(false);
  
  var [reviews, setReviews] = useState([]);
  var [reviewRating, setReviewRating] = useState(5);
  var [reviewContent, setReviewContent] = useState('');
  var [reviewError, setReviewError] = useState('');
  var [isSubmitting, setIsSubmitting] = useState(false);
  var [hasUserReview, setHasUserReview] = useState(false);
  
  var currentUserId = user ? user.id : null;
  
  useEffect(function() {
    loadMusic();
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
  
  function handleSubmitReview() {
    if (!reviewContent.trim()) {
      setReviewError('Please write a review');
      return;
    }
    
    setIsSubmitting(true);
    setReviewError('');
    
    api.post('/music/' + id + '/reviews', {
      rating: reviewRating,
      content: reviewContent.trim()
    }).then(function() {
      setReviewContent('');
      setReviewRating(5);
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
  
  function createStarClickHandler(starValue) {
    return function() {
      setReviewRating(starValue);
    };
  }
  
  function renderStars(rating, interactive) {
    var stars = [];
    for (var i = 1; i <= 5; i++) {
      if (interactive) {
        stars.push(
          <button 
            key={i} 
            type="button"
            className="star-btn"
            onClick={createStarClickHandler(i)}
          >
            <Star size={20} fill={i <= reviewRating ? '#fbbf24' : 'none'} color={i <= reviewRating ? '#fbbf24' : '#d1d5db'} />
          </button>
        );
      } else {
        stars.push(
          <Star key={i} size={16} fill={i <= rating ? '#fbbf24' : 'none'} color={i <= rating ? '#fbbf24' : '#d1d5db'} />
        );
      }
    }
    return stars;
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
            <div className="review-rating-input">
              <span>Your Rating:</span>
              <div className="stars-input">{renderStars(reviewRating, true)}</div>
            </div>
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
                      <User size={16} />
                      {review.username}
                    </span>
                    <div className="review-stars">{renderStars(review.rating, false)}</div>
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
