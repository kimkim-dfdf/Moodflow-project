import { useState, useEffect } from 'react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { Target, Users, Check, Plus, Trash2, X } from 'lucide-react';

function Challenge() {
  var { user } = useAuth();
  var [challenges, setChallenges] = useState([]);
  var [loading, setLoading] = useState(true);
  var [showCreateModal, setShowCreateModal] = useState(false);
  var [newTitle, setNewTitle] = useState('');
  var [newDescription, setNewDescription] = useState('');
  var [newEmoji, setNewEmoji] = useState('🎯');
  var [creating, setCreating] = useState(false);

  var emojiOptions = ['🎯', '💪', '🏃', '📚', '🧘', '💧', '🌟', '🎨', '🎵', '❤️', '🌈', '✨'];

  useEffect(function() {
    loadChallenges();
  }, []);

  function loadChallenges() {
    setLoading(true);
    api.get('/challenges').then(function(res) {
      setChallenges(res.data);
      setLoading(false);
    }).catch(function() {
      setLoading(false);
    });
  }

  function handleJoin(challengeId) {
    api.post('/challenges/' + challengeId + '/join').then(function() {
      loadChallenges();
    }).catch(function(err) {
      console.log('Join error:', err);
    });
  }

  function handleComplete(challengeId) {
    api.post('/challenges/' + challengeId + '/complete').then(function() {
      loadChallenges();
    }).catch(function(err) {
      console.log('Complete error:', err);
    });
  }

  function handleDelete(challengeId) {
    if (confirm('Are you sure you want to delete this challenge?')) {
      api.delete('/challenges/' + challengeId).then(function() {
        loadChallenges();
      }).catch(function(err) {
        console.log('Delete error:', err);
      });
    }
  }

  function handleCreate() {
    if (!newTitle.trim()) {
      return;
    }

    setCreating(true);
    api.post('/challenges', {
      title: newTitle,
      description: newDescription,
      emoji: newEmoji
    }).then(function() {
      setNewTitle('');
      setNewDescription('');
      setNewEmoji('🎯');
      setShowCreateModal(false);
      setCreating(false);
      loadChallenges();
    }).catch(function() {
      setCreating(false);
    });
  }

  function closeModal() {
    setShowCreateModal(false);
    setNewTitle('');
    setNewDescription('');
    setNewEmoji('🎯');
  }

  if (loading) {
    return (
      <div className="challenge-page">
        <p>Loading challenges...</p>
      </div>
    );
  }

  return (
    <div className="challenge-page">
      <div className="challenge-header">
        <div className="challenge-title-section">
          <h1><Target size={28} /> Community Challenges</h1>
          <p className="challenge-subtitle">Join challenges and complete them with other users!</p>
        </div>
        <button className="create-challenge-btn" onClick={function() { setShowCreateModal(true); }}>
          <Plus size={20} />
          Create Challenge
        </button>
      </div>

      {challenges.length === 0 ? (
        <div className="no-challenges">
          <Target size={48} />
          <h3>No challenges yet</h3>
          <p>Be the first to create a challenge!</p>
        </div>
      ) : (
        <div className="challenges-grid">
          {challenges.map(function(challenge) {
            var isCreator = Number(challenge.creator_id) === Number(user.id);
            
            return (
              <div key={challenge.id} className={'challenge-card ' + (challenge.user_completed ? 'completed' : '')}>
                <div className="challenge-card-header">
                  <span className="challenge-emoji">{challenge.emoji}</span>
                  <div className="challenge-card-info">
                    <h3 className="challenge-card-title">{challenge.title}</h3>
                    <p className="challenge-creator">by {challenge.creator_name}</p>
                  </div>
                  {isCreator && (
                    <button className="delete-challenge-btn" onClick={function() { handleDelete(challenge.id); }}>
                      <Trash2 size={16} />
                    </button>
                  )}
                </div>
                
                {challenge.description && (
                  <p className="challenge-description">{challenge.description}</p>
                )}
                
                <div className="challenge-stats">
                  <div className="stat-item">
                    <Users size={16} />
                    <span>{challenge.participant_count} joined</span>
                  </div>
                  <div className="stat-item">
                    <Check size={16} />
                    <span>{challenge.completed_count} completed</span>
                  </div>
                </div>

                <div className="challenge-actions">
                  {!challenge.user_joined ? (
                    <button className="join-btn" onClick={function() { handleJoin(challenge.id); }}>
                      Join Challenge
                    </button>
                  ) : challenge.user_completed ? (
                    <button className="completed-btn" disabled>
                      <Check size={18} /> Completed!
                    </button>
                  ) : (
                    <button className="complete-btn" onClick={function() { handleComplete(challenge.id); }}>
                      Mark as Complete
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {showCreateModal && (
        <div className="modal-overlay" onClick={function(e) { if (e.target.className === 'modal-overlay') closeModal(); }}>
          <div className="create-challenge-modal">
            <div className="modal-header-row">
              <h2>Create New Challenge</h2>
              <button className="modal-close-btn" onClick={closeModal}>
                <X size={24} />
              </button>
            </div>

            <div className="form-group">
              <label>Choose an Emoji</label>
              <div className="emoji-picker">
                {emojiOptions.map(function(emoji) {
                  return (
                    <button
                      key={emoji}
                      className={'emoji-option ' + (newEmoji === emoji ? 'selected' : '')}
                      onClick={function() { setNewEmoji(emoji); }}
                    >
                      {emoji}
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="form-group">
              <label>Challenge Title *</label>
              <input
                type="text"
                value={newTitle}
                onChange={function(e) { setNewTitle(e.target.value); }}
                placeholder="e.g., Drink 8 glasses of water today"
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label>Description (optional)</label>
              <textarea
                value={newDescription}
                onChange={function(e) { setNewDescription(e.target.value); }}
                placeholder="Add more details about the challenge..."
                className="form-textarea"
                rows={3}
              />
            </div>

            <div className="modal-actions">
              <button className="cancel-btn" onClick={closeModal}>Cancel</button>
              <button 
                className="submit-btn" 
                onClick={handleCreate}
                disabled={creating || !newTitle.trim()}
              >
                {creating ? 'Creating...' : 'Create Challenge'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Challenge;
