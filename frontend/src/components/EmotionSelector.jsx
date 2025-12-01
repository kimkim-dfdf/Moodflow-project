/**
 * 감정 선택 컴포넌트
 * - 6가지 감정(Happy, Sad, Angry, Stressed, Tired, Neutral) 중 하나 선택
 * - 선택하면 바로 서버에 기록됨
 */

import { useState, useEffect } from 'react';
import api from '../api/axios';


const EmotionSelector = ({ selectedEmotion, onSelect }) => {
  // 사용 가능한 감정 목록
  const [emotions, setEmotions] = useState([]);
  const [loading, setLoading] = useState(true);


  // 컴포넌트 마운트 시 감정 목록 가져오기
  useEffect(() => {
    fetchEmotions();
  }, []);


  /**
   * 서버에서 감정 목록 가져오기
   */
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


  /**
   * 감정 선택 처리
   * - 서버에 기록하고 부모 컴포넌트에 알림
   */
  const handleSelect = async (emotion) => {
    try {
      await api.post('/emotions/record', { 
        emotion_id: emotion.id 
      });
      onSelect(emotion);
    } catch (error) {
      console.error('Failed to record emotion:', error);
    }
  };


  // 로딩 중
  if (loading) {
    return <div className="emotion-selector loading">Loading emotions...</div>;
  }


  return (
    <div className="emotion-selector">
      <div className="emotion-grid">
        {emotions.map((emotion) => {
          const isSelected = selectedEmotion?.id === emotion.id;
          
          return (
            <button
              key={emotion.id}
              className={`emotion-btn ${isSelected ? 'selected' : ''}`}
              style={{ 
                '--emotion-color': emotion.color,
                backgroundColor: isSelected ? emotion.color : 'transparent'
              }}
              onClick={() => handleSelect(emotion)}
            >
              <span className="emotion-emoji">{emotion.emoji}</span>
              <span className="emotion-name">{emotion.name}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default EmotionSelector;
