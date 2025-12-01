import { useState, useEffect } from 'react';
import api from '../api/axios';
import { Lock } from 'lucide-react';

const EmotionSelector = ({ selectedEmotion, onSelect, locked = false }) => {
  const [emotions, setEmotions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEmotions();
  }, []);

  const fetchEmotions = async () => {
    try {
      const response = await api.get('/emotions');
      setEmotions(response.data);
    } catch (error) {
      console.error('Failed to fetch emotions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = async (emotion) => {
    if (locked || selectedEmotion) return;
    
    try {
      await api.post('/emotions/record', { emotion_id: emotion.id });
      onSelect(emotion);
    } catch (error) {
      console.error('Failed to record emotion:', error);
    }
  };

  if (loading) {
    return <div className="emotion-selector loading">Loading emotions...</div>;
  }

  const isLocked = locked || selectedEmotion !== null;

  return (
    <div className={`emotion-selector ${isLocked ? 'locked' : ''}`}>
      {isLocked && selectedEmotion && (
        <div className="emotion-locked-message">
          <Lock size={14} />
          <span>Today's mood has been recorded</span>
        </div>
      )}
      <div className="emotion-grid">
        {emotions.map((emotion) => {
          const isSelected = selectedEmotion?.id === emotion.id;
          const isDisabled = isLocked && !isSelected;
          
          return (
            <button
              key={emotion.id}
              className={`emotion-btn ${isSelected ? 'selected' : ''} ${isDisabled ? 'disabled' : ''}`}
              style={{ 
                '--emotion-color': emotion.color,
                backgroundColor: isSelected ? emotion.color : 'transparent',
                opacity: isDisabled ? 0.4 : 1,
                cursor: isLocked ? 'default' : 'pointer'
              }}
              onClick={() => handleSelect(emotion)}
              disabled={isDisabled}
            >
              <span className="emotion-emoji">{emotion.emoji}</span>
              <span className="emotion-name">{emotion.name}</span>
              {isSelected && isLocked && (
                <Lock size={12} className="lock-icon" />
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default EmotionSelector;
