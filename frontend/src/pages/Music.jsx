import { useState, useEffect, useRef } from 'react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { Music as MusicIcon, Search, Heart, Play, X, User, Trash2, Tag } from 'lucide-react';

// YouTube URL에서 비디오 ID 추출
function getYoutubeVideoId(url) {
  if (!url) return null;
  if (url.indexOf('youtu.be/') !== -1) {
    var parts = url.split('youtu.be/');
    if (parts.length > 1) return parts[1].split('?')[0].split('&')[0];
  } else if (url.indexOf('youtube.com/watch') !== -1) {
    var queryString = url.split('?')[1];
    if (queryString) {
      var params = queryString.split('&');
      for (var i = 0; i < params.length; i++) {
        if (params[i].indexOf('v=') === 0) return params[i].substring(2);
      }
    }
  }
  return null;
}

// 음악 카드 컴포넌트
function MusicCard(props) {
  var music = props.music;
  var isFavorite = props.isFavorite || false;
  var [imgError, setImgError] = useState(false);
  
  var videoId = getYoutubeVideoId(music.youtube_url);
  var thumbnailUrl = videoId ? 'https://img.youtube.com/vi/' + videoId + '/mqdefault.jpg' : null;
  
  return (
    <div className="music-page-card" onClick={function() { if (props.onSelect) props.onSelect(music); }} style={{cursor: 'pointer'}}>
      <div className="music-thumbnail">
        {thumbnailUrl && !imgError ? (
          <img src={thumbnailUrl} alt={music.title} onError={function() { setImgError(true); }} className="music-thumbnail-img" />
        ) : (
          <div className="music-page-icon"><MusicIcon size={24} /></div>
        )}
      </div>
      <div className="music-page-info">
        <div className="music-title-row">
          <h4 className="music-page-title">{music.title}</h4>
          <button className={'music-favorite-btn ' + (isFavorite ? 'active' : '')} onClick={function(e) { e.stopPropagation(); if (props.onToggleFavorite) props.onToggleFavorite(music.id); }}>
            <Heart size={18} fill={isFavorite ? '#ef4444' : 'none'} />
          </button>
        </div>
        <p className="music-page-artist">{music.artist}</p>
        <div className="music-page-meta">
          <span className="music-page-genre">{music.genre}</span>
          {music.emotion && <span className="music-page-emotion">{music.emotion}</span>}
        </div>
      </div>
      {music.youtube_url && <a href={music.youtube_url} target="_blank" rel="noopener noreferrer" className="music-youtube-btn" onClick={function(e) { e.stopPropagation(); }}><Play size={16} />YouTube</a>}
    </div>
  );
}

// 로컬 스토리지 헬퍼
function getFavorites() { try { var s = localStorage.getItem('music_favorites'); if (s) return JSON.parse(s); } catch (e) {} return []; }
function saveFavorites(ids) { try { localStorage.setItem('music_favorites', JSON.stringify(ids)); } catch (e) {} }

// 음악 상세 뷰
function MusicDetailView(props) {
  var music = props.music;
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
      var hasReview = false;
      for (var i = 0; i < res.data.length; i++) {
        if (Number(res.data[i].user_id) === Number(currentUserId)) { hasReview = true; break; }
      }
      setHasUserReview(hasReview);
    }).catch(function() { setReviews([]); });
  }
  
  function loadTags() {
    api.get('/music/' + music.id + '/tags').then(function(res) { setListeningTags(res.data); }).catch(function() { setListeningTags([]); });
  }
  
  function isFavorite(musicId) {
    for (var i = 0; i < props.favoriteIds.length; i++) { if (props.favoriteIds[i] === musicId) return true; }
    return false;
  }
  
  function handleTagClick(tag) {
    if (tag.user_tagged) {
      api.delete('/music/' + music.id + '/tags/' + tag.id).then(loadTags);
    } else {
      api.post('/music/' + music.id + '/tags/' + tag.id).then(loadTags);
    }
  }
  
  function handleSubmitReview() {
    if (!reviewContent.trim()) { setReviewError('Please write a review'); return; }
    setIsSubmitting(true);
    api.post('/music/' + music.id + '/reviews', { content: reviewContent.trim() }).then(function() {
      setReviewContent('');
      loadReviews();
      setIsSubmitting(false);
    }).catch(function(err) {
      setReviewError(err.response?.data?.error || 'Failed');
      setIsSubmitting(false);
    });
  }
  
  function handleDeleteReview(reviewId) { api.delete('/music/reviews/' + reviewId).then(loadReviews); }
  
  var thumbnailUrl = null;
  if (music && music.youtube_url) {
    var videoId = getYoutubeVideoId(music.youtube_url);
    if (videoId) thumbnailUrl = 'https://img.youtube.com/vi/' + videoId + '/mqdefault.jpg';
  }
  
  return (
    <div className="music-detail-inline">
      <div className="music-detail-header">
        <div className="music-detail-thumbnail">
          {thumbnailUrl && !thumbnailError ? (
            <img src={thumbnailUrl} alt={music.title} onError={function() { setThumbnailError(true); }} className="music-detail-thumbnail-img" />
          ) : (
            <div className="music-detail-icon"><MusicIcon size={48} /></div>
          )}
        </div>
        <div className="music-detail-info">
          <h2>{music.title}</h2>
          <p className="music-detail-artist">{music.artist}</p>
          <div className="music-detail-meta">
            <span className="music-detail-genre">{music.genre}</span>
            {music.emotion && <span className="music-detail-emotion">Mood: {music.emotion}</span>}
          </div>
        </div>
      </div>
      
      <div className="music-detail-actions">
        <button className={'favorite-btn-large ' + (isFavorite(music.id) ? 'active' : '')} onClick={function() { props.onToggleFavorite(music.id); }}>
          <Heart size={18} fill={isFavorite(music.id) ? '#ef4444' : 'none'} />
          {isFavorite(music.id) ? 'Remove from Favorites' : 'Add to Favorites'}
        </button>
        {music.youtube_url && <a href={music.youtube_url} target="_blank" rel="noopener noreferrer" className="youtube-btn-large"><Play size={18} />Watch on YouTube</a>}
      </div>
      
      <div className="music-detail-reviews">
        <h4>Reviews ({reviews.length})</h4>
        
        {!hasUserReview && (
          <div className="review-form">
            <div className="music-listening-tags">
              <h4><Tag size={16} /> Listening Tags</h4>
              <p className="listening-tags-hint">Click tags to describe when you listen</p>
              <div className="listening-tags-list">
                {listeningTags.map(function(tag) {
                  return <button key={tag.id} className={'listening-tag-btn ' + (tag.user_tagged ? 'active' : '')} onClick={function() { handleTagClick(tag); }}>{tag.name}{tag.count > 0 && <span className="tag-count">{tag.count}</span>}</button>;
                })}
              </div>
            </div>
            <textarea className="review-textarea" placeholder="Write your review..." value={reviewContent} onChange={function(e) { setReviewContent(e.target.value); }} rows={3} />
            {reviewError && <div className="review-error">{reviewError}</div>}
            <button className="review-submit-btn" onClick={handleSubmitReview} disabled={isSubmitting}>{isSubmitting ? 'Submitting...' : 'Submit Review'}</button>
          </div>
        )}
        
        {hasUserReview && <div className="review-notice">You have already reviewed this music.</div>}
        
        <div className="reviews-list">
          {reviews.length === 0 ? <p className="no-reviews">No reviews yet.</p> : reviews.map(function(review) {
            return (
              <div key={review.id} className="review-item">
                <div className="review-header">
                  <span className="review-user"><User size={14} />{review.username}</span>
                  {Number(review.user_id) === Number(currentUserId) && <button className="review-delete-btn" onClick={function() { handleDeleteReview(review.id); }}><Trash2 size={14} /></button>}
                </div>
                {review.listening_tags && review.listening_tags.length > 0 && (
                  <div className="review-tags">{review.listening_tags.map(function(tagName, idx) { return <span key={idx} className="review-tag">{tagName}</span>; })}</div>
                )}
                <p className="review-content">{review.content}</p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// 메인 Music 컴포넌트
function Music() {
  var [allMusic, setAllMusic] = useState([]);
  var [filteredMusic, setFilteredMusic] = useState([]);
  var [emotions, setEmotions] = useState([]);
  var [selectedEmotion, setSelectedEmotion] = useState('');
  var [loading, setLoading] = useState(true);
  var [favoriteIds, setFavoriteIds] = useState(getFavorites());
  var [searchQuery, setSearchQuery] = useState('');
  var [activeTab, setActiveTab] = useState('all');
  var [selectedMusic, setSelectedMusic] = useState(null);
  var searchTimeoutRef = useRef(null);

  useEffect(function() {
    Promise.all([api.get('/music/all'), api.get('/emotions')]).then(function(results) {
      setAllMusic(results[0].data);
      setFilteredMusic(results[0].data);
      setEmotions(results[1].data);
      setLoading(false);
    }).catch(function() { setLoading(false); });
  }, []);

  function handleEmotionFilter(emotionName) {
    if (selectedEmotion === emotionName) {
      setSelectedEmotion('');
      setFilteredMusic(allMusic);
    } else {
      setSelectedEmotion(emotionName);
      var filtered = [];
      for (var i = 0; i < allMusic.length; i++) { if (allMusic[i].emotion === emotionName) filtered.push(allMusic[i]); }
      setFilteredMusic(filtered);
    }
  }

  function handleSearch(query) {
    setSearchQuery(query);
    if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current);
    if (!query.trim()) {
      if (selectedEmotion) {
        var emotionFiltered = [];
        for (var i = 0; i < allMusic.length; i++) { if (allMusic[i].emotion === selectedEmotion) emotionFiltered.push(allMusic[i]); }
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
        var m = allMusic[i];
        if (m.title.toLowerCase().indexOf(searchLower) >= 0 || m.artist.toLowerCase().indexOf(searchLower) >= 0 || (m.genre && m.genre.toLowerCase().indexOf(searchLower) >= 0)) {
          if (!selectedEmotion || m.emotion === selectedEmotion) results.push(m);
        }
      }
      setFilteredMusic(results);
    }, 300);
  }

  function clearSearch() {
    setSearchQuery('');
    if (selectedEmotion) {
      var emotionFiltered = [];
      for (var i = 0; i < allMusic.length; i++) { if (allMusic[i].emotion === selectedEmotion) emotionFiltered.push(allMusic[i]); }
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
      for (var i = 0; i < favoriteIds.length; i++) { if (favoriteIds[i] !== musicId) newIds.push(favoriteIds[i]); }
    } else {
      newIds = favoriteIds.concat([musicId]);
    }
    setFavoriteIds(newIds);
    saveFavorites(newIds);
  }

  function isFavorite(musicId) { return favoriteIds.indexOf(musicId) >= 0; }

  function handleTabChange(tab) {
    setActiveTab(tab);
    setSearchQuery('');
    setSelectedEmotion('');
    setFilteredMusic(allMusic);
    setSelectedMusic(null);
  }

  function getDisplayMusic() {
    if (activeTab === 'favorites') {
      var favMusic = [];
      for (var i = 0; i < allMusic.length; i++) { if (favoriteIds.indexOf(allMusic[i].id) >= 0) favMusic.push(allMusic[i]); }
      if (searchQuery.trim()) {
        var searchLower = searchQuery.toLowerCase();
        var results = [];
        for (var j = 0; j < favMusic.length; j++) {
          var m = favMusic[j];
          if (m.title.toLowerCase().indexOf(searchLower) >= 0 || m.artist.toLowerCase().indexOf(searchLower) >= 0) results.push(m);
        }
        return results;
      }
      return favMusic;
    }
    return filteredMusic;
  }

  var displayMusic = getDisplayMusic();

  return (
    <div className="music-page">
      <header className="page-header"><h1><MusicIcon size={28} /> Music Recommendations</h1><p>Discover music that matches your mood</p></header>

      <div className="music-search-section">
        <div className="search-input-wrapper">
          <Search size={20} className="search-icon" />
          <input type="text" className="music-search-input" placeholder="Search by title, artist, or genre..." value={searchQuery} onChange={function(e) { handleSearch(e.target.value); }} />
          {searchQuery && <button className="search-clear-btn" onClick={clearSearch}><X size={18} /></button>}
        </div>
      </div>

      <div className="music-tabs">
        <button className={'music-tab ' + (activeTab === 'all' ? 'active' : '')} onClick={function() { handleTabChange('all'); }}><MusicIcon size={18} />All Music</button>
        <button className={'music-tab ' + (activeTab === 'favorites' ? 'active' : '')} onClick={function() { handleTabChange('favorites'); }}><Heart size={18} />Favorites ({favoriteIds.length})</button>
      </div>

      {activeTab === 'all' && !searchQuery && !selectedMusic && (
        <div className="emotion-filter-section">
          <div className="emotion-filter-header">
            <span className="emotion-filter-label">Filter by Mood</span>
            {selectedEmotion && <button className="clear-emotion-btn" onClick={function() { setSelectedEmotion(''); setFilteredMusic(allMusic); }}>Clear</button>}
          </div>
          <div className="emotion-chips-container">
            {emotions.map(function(emotion) {
              var isActive = selectedEmotion === emotion.name;
              return <button key={emotion.id} className={'emotion-chip ' + (isActive ? 'active' : '')} onClick={function() { handleEmotionFilter(emotion.name); }} style={isActive ? { backgroundColor: emotion.color, borderColor: emotion.color } : {}}><span>{emotion.emoji}</span>{emotion.name}</button>;
            })}
          </div>
        </div>
      )}

      {selectedMusic ? (
        <MusicDetailView music={selectedMusic} favoriteIds={favoriteIds} onToggleFavorite={toggleFavorite} />
      ) : loading ? (
        <div className="loading-state">Loading music...</div>
      ) : (
        <div className="music-container">
          {displayMusic.length > 0 ? (
            <>
              <div className="music-result-info">{searchQuery ? displayMusic.length + ' results for "' + searchQuery + '"' : activeTab === 'favorites' ? displayMusic.length + ' favorites' : selectedEmotion ? displayMusic.length + ' songs for "' + selectedEmotion + '"' : 'All ' + displayMusic.length + ' songs'}</div>
              <div className="music-full-grid">
                {displayMusic.map(function(music) { return <MusicCard key={music.id} music={music} isFavorite={isFavorite(music.id)} onToggleFavorite={toggleFavorite} onSelect={function(m) { setSelectedMusic(m); }} />; })}
              </div>
            </>
          ) : (
            <div className="empty-state"><MusicIcon size={48} />{searchQuery ? <p>No music found for "{searchQuery}"</p> : activeTab === 'favorites' ? <p>No favorites yet.</p> : <p>No music found.</p>}</div>
          )}
        </div>
      )}
    </div>
  );
}

export default Music;
