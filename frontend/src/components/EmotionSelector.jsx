import { useState, useEffect } from 'react';
import api from '../api/axios';

const EmotionSelector = ({ selectedEmotion, onSelect }) => {
  const [emotions, setEmotions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [useAnalyzer, setUseAnalyzer] = useState(false);
  
  const [factors, setFactors] = useState({
    sleep_quality: 3,
    energy_level: 3,
    stress_level: 3,
    concentration: 3,
    motivation: 3,
    mood_rating: 3
  });

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

  const handleFactorChange = (factor, value) => {
    setFactors(prev => ({
      ...prev,
      [factor]: parseInt(value)
    }));
  };

  const handleAnalyze = async () => {
    try {
      const response = await api.post('/emotions/analyze', factors);
      const emotionId = response.data.emotion_id;
      const emotion = emotions.find(e => e.id === emotionId);
      
      if (emotion) {
        await api.post('/emotions/record', {
          emotion_id: emotion.id,
          ...factors
        });
        onSelect(emotion);
        setUseAnalyzer(false);
      }
    } catch (error) {
      console.error('Failed to analyze mood:', error);
    }
  };

  const handleDirectSelect = async (emotion) => {
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
      <h3>How are you feeling today?</h3>
      
      {!useAnalyzer ? (
        <>
          <div className="emotion-grid">
            {emotions.map((emotion) => (
              <button
                key={emotion.id}
                className={`emotion-btn ${selectedEmotion?.id === emotion.id ? 'selected' : ''}`}
                style={{ 
                  '--emotion-color': emotion.color,
                  backgroundColor: selectedEmotion?.id === emotion.id ? emotion.color : 'transparent'
                }}
                onClick={() => handleDirectSelect(emotion)}
              >
                <span className="emotion-emoji">{emotion.emoji}</span>
                <span className="emotion-name">{emotion.name}</span>
              </button>
            ))}
          </div>
          <button 
            className="emotion-analyze-btn"
            onClick={() => setUseAnalyzer(true)}
          >
            분석해서 감정 정하기
          </button>
        </>
      ) : (
        <div className="emotion-analyzer-form">
          <div className="factors-grid">
            <div className="factor-item">
              <label>수면 퀄리티</label>
              <input
                type="range"
                min="1"
                max="5"
                value={factors.sleep_quality}
                onChange={(e) => handleFactorChange('sleep_quality', e.target.value)}
                className="factor-slider"
              />
              <span className="factor-value">{factors.sleep_quality}</span>
            </div>
            
            <div className="factor-item">
              <label>에너지 레벨</label>
              <input
                type="range"
                min="1"
                max="5"
                value={factors.energy_level}
                onChange={(e) => handleFactorChange('energy_level', e.target.value)}
                className="factor-slider"
              />
              <span className="factor-value">{factors.energy_level}</span>
            </div>
            
            <div className="factor-item">
              <label>예민도</label>
              <input
                type="range"
                min="1"
                max="5"
                value={factors.stress_level}
                onChange={(e) => handleFactorChange('stress_level', e.target.value)}
                className="factor-slider"
              />
              <span className="factor-value">{factors.stress_level}</span>
            </div>
            
            <div className="factor-item">
              <label>집중력</label>
              <input
                type="range"
                min="1"
                max="5"
                value={factors.concentration}
                onChange={(e) => handleFactorChange('concentration', e.target.value)}
                className="factor-slider"
              />
              <span className="factor-value">{factors.concentration}</span>
            </div>
            
            <div className="factor-item">
              <label>동기부여</label>
              <input
                type="range"
                min="1"
                max="5"
                value={factors.motivation}
                onChange={(e) => handleFactorChange('motivation', e.target.value)}
                className="factor-slider"
              />
              <span className="factor-value">{factors.motivation}</span>
            </div>
            
            <div className="factor-item">
              <label>기분</label>
              <input
                type="range"
                min="1"
                max="5"
                value={factors.mood_rating}
                onChange={(e) => handleFactorChange('mood_rating', e.target.value)}
                className="factor-slider"
              />
              <span className="factor-value">{factors.mood_rating}</span>
            </div>
          </div>
          
          <div className="analyzer-buttons">
            <button className="btn-analyze" onClick={handleAnalyze}>
              감정 분석
            </button>
            <button className="btn-cancel" onClick={() => setUseAnalyzer(false)}>
              취소
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default EmotionSelector;
