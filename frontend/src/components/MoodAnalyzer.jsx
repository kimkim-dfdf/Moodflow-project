import { useState, useEffect } from 'react';
import api from '../api/axios';
import { Sparkles } from 'lucide-react';

const MoodAnalyzer = ({ selectedEmotion, onSelect }) => {
  const [emotions, setEmotions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAnalyzer, setShowAnalyzer] = useState(false);
  
  const [factors, setFactors] = useState({
    sleep_quality: 3,
    mood_rating: 3,
    energy_level: 3,
    stress_level: 3,
    concentration: 3,
    motivation: 3
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

  const handleAnalyzeMood = async () => {
    try {
      const response = await api.post('/emotions/analyze', factors);
      const emotionId = response.data.emotion_id;
      
      const selectedEmotion = emotions.find(e => e.id === emotionId);
      if (selectedEmotion) {
        await handleRecordEmotion(selectedEmotion);
        setShowAnalyzer(false);
      }
    } catch (error) {
      console.error('Failed to analyze mood:', error);
    }
  };

  const handleRecordEmotion = async (emotion) => {
    try {
      await api.post('/emotions/record', {
        emotion_id: emotion.id,
        ...factors
      });
      onSelect(emotion);
    } catch (error) {
      console.error('Failed to record emotion:', error);
    }
  };

  const handleDirectSelect = async (emotion) => {
    await handleRecordEmotion(emotion);
  };

  const getFactorLabel = (factor) => {
    const labels = {
      sleep_quality: 'Sleep Quality',
      mood_rating: 'Today\'s Mood',
      energy_level: 'Energy Level',
      stress_level: 'Stress Level',
      concentration: 'Concentration',
      motivation: 'Motivation'
    };
    return labels[factor] || factor;
  };

  const getFactorEmoji = (factor, value) => {
    if (factor === 'stress_level') {
      // For stress, higher is worse
      if (value <= 2) return '😌';
      if (value <= 3) return '😐';
      return '😰';
    }
    // For others, higher is better
    if (value <= 2) return '😫';
    if (value <= 3) return '😐';
    return '😊';
  };

  if (loading) {
    return <div className="mood-analyzer loading">Loading emotions...</div>;
  }

  return (
    <div className="mood-analyzer-container">
      <div className="emotion-selector">
        <h3>How are you feeling today?</h3>
        
        {!showAnalyzer ? (
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
              className="analyze-btn"
              onClick={() => setShowAnalyzer(true)}
            >
              <Sparkles size={16} />
              Let me analyze my mood
            </button>
          </>
        ) : (
          <div className="mood-analysis-form">
            <p className="form-intro">Answer a few quick questions to get an AI suggestion for your mood</p>
            
            <div className="factors-grid">
              {Object.entries(factors).map(([factor, value]) => (
                <div key={factor} className="factor-input">
                  <div className="factor-header">
                    <label>{getFactorLabel(factor)}</label>
                    <span className="factor-emoji">{getFactorEmoji(factor, value)}</span>
                  </div>
                  <div className="slider-container">
                    <input
                      type="range"
                      min="1"
                      max="5"
                      value={value}
                      onChange={(e) => handleFactorChange(factor, e.target.value)}
                      className="slider"
                    />
                    <div className="slider-labels">
                      <span>Low</span>
                      <span className="value-display">{value}</span>
                      <span>High</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="form-actions">
              <button 
                className="analyze-submit-btn"
                onClick={handleAnalyzeMood}
              >
                Analyze & Set Mood
              </button>
              <button 
                className="analyze-cancel-btn"
                onClick={() => setShowAnalyzer(false)}
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MoodAnalyzer;
