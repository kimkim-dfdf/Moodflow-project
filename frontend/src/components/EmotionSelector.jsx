import { useState, useEffect } from 'react';
import api from '../api/axios';

function EmotionSelector(props) {
  var selectedEmotion = props.selectedEmotion;
  var onSelect = props.onSelect;
  
  const [emotions, setEmotions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(function() {
    api.get('/emotions').then(function(res) {
      setEmotions(res.data);
      setLoading(false);
    }).catch(function(err) {
      console.error('Failed:', err);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return <div className="emotion-selector">Loading...</div>;
  }

  return (
    <div className="emotion-selector">
      <div className="emotion-grid">
        {emotions.map(function(emotion) {
          var isSelected = selectedEmotion && selectedEmotion.id === emotion.id;
          return (
            <button key={emotion.id} className={'emotion-btn ' + (isSelected ? 'selected' : '')} style={{ borderColor: emotion.color, backgroundColor: isSelected ? emotion.color : 'white' }} onClick={function() { onSelect(emotion); }}>
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
