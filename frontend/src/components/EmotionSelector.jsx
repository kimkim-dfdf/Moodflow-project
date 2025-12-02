import { useState, useEffect } from 'react';
import api from '../api/axios';

function EmotionSelector({ selectedEmotion, onSelect }) {
  const [emotions, setEmotions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/emotions')
      .then(response => {
        setEmotions(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Failed to fetch emotions:', error);
        setLoading(false);
      });
  }, []);

  function handleClick(emotion) {
    onSelect(emotion);
  }

  if (loading) {
    return <div className="emotion-selector">Loading...</div>;
  }

  return (
    <div className="emotion-selector">
      <div className="emotion-grid">
        {emotions.map(function(emotion) {
          const isSelected = selectedEmotion && selectedEmotion.id === emotion.id;
          
          return (
            <button
              key={emotion.id}
              className={isSelected ? 'emotion-btn selected' : 'emotion-btn'}
              style={{ 
                borderColor: emotion.color,
                backgroundColor: isSelected ? emotion.color : 'white'
              }}
              onClick={function() { handleClick(emotion); }}
            >
              <span className="emotion-emoji">{emotion.emoji}</span>
              <span className="emotion-name">{emotion.name}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

export default EmotionSelector;
