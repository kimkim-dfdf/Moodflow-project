import { useState, useEffect } from 'react';
import { format, isToday } from 'date-fns';
import api from '../api/axios';

const EmotionSelector = ({ selectedEmotion, onSelect, selectedDate, onEmotionRecorded }) => {
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
      const dateStr = selectedDate ? format(selectedDate, 'yyyy-MM-dd') : format(new Date(), 'yyyy-MM-dd');
      await api.post('/emotions/record', { 
        emotion_id: emotion.id,
        date: dateStr
      });
      onSelect(emotion);
      if (onEmotionRecorded) {
        onEmotionRecorded();
      }
    } catch (error) {
      console.error('Failed to record emotion:', error);
    }
  };

  const getDateLabel = () => {
    if (!selectedDate || isToday(selectedDate)) {
      return 'How are you feeling today?';
    }
    return `${format(selectedDate, 'M월 d일')}의 기분은 어땠나요?`;
  };

  if (loading) {
    return <div className="emotion-selector loading">Loading emotions...</div>;
  }

  return (
    <div className="emotion-selector">
      <h3>{getDateLabel()}</h3>
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
