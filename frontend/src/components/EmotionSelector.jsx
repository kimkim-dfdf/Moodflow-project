import { useState, useEffect } from 'react';
import api from '../api/axios';

const EmotionSelector = ({ selectedEmotion, onSelect }) => {
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

  return (
    <div className="emotion-selector">
      <div className="emotion-grid">
        {emotions.map((emotion) => (
          <button
            key={emotion.id}
            className={`emotion-btn ${selectedEmotion?.id === emotion.id ? 'selected' : ''}`}
            style={{ 
              '--emotion-color': emotion.color,
              backgroundColor: selectedEmotion?.id === emotion.id ? emotion.color : 'transparent'
            }}
            onClick={() => handleSelect(emotion)}
          >
            <span className="emotion-emoji">{emotion.emoji}</span>
            <span className="emotion-name">{emotion.name}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default EmotionSelector;
