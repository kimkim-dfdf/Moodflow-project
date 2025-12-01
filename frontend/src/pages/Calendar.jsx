import { useState, useEffect } from 'react';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isToday, startOfWeek, endOfWeek } from 'date-fns';
import { ChevronLeft, ChevronRight, X, Camera, Image, Trash2 } from 'lucide-react';
import api from '../api/axios';

const Calendar = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [emotionData, setEmotionData] = useState({});
  const [selectedDate, setSelectedDate] = useState(null);
  const [emotions, setEmotions] = useState([]);
  const [showDiaryModal, setShowDiaryModal] = useState(false);
  const [diaryEntry, setDiaryEntry] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const [formData, setFormData] = useState({
    emotion_id: null,
    notes: '',
    photo_url: ''
  });

  const [photoPreview, setPhotoPreview] = useState(null);
  const [uploadingPhoto, setUploadingPhoto] = useState(false);

  useEffect(() => {
    fetchEmotionData();
    fetchEmotions();
  }, [currentDate]);

  const fetchEmotionData = async () => {
    try {
      const response = await api.get('/emotions/statistics', { params: { days: 60 } });
      setEmotionData(response.data.daily_emotions || {});
    } catch (error) {
      console.error('Failed to fetch emotion data:', error);
    }
  };

  const fetchEmotions = async () => {
    try {
      const response = await api.get('/emotions');
      setEmotions(response.data);
    } catch (error) {
      console.error('Failed to fetch emotions:', error);
    }
  };

  const fetchDiaryEntry = async (date) => {
    try {
      setIsLoading(true);
      const dateStr = format(date, 'yyyy-MM-dd');
      const response = await api.get(`/emotions/diary/${dateStr}`);
      if (response.data) {
        setDiaryEntry(response.data);
        setFormData({
          emotion_id: response.data.emotion_id,
          notes: response.data.notes || '',
          photo_url: response.data.photo_url || ''
        });
        setPhotoPreview(response.data.photo_url ? `${api.defaults.baseURL}${response.data.photo_url}` : null);
      } else {
        setDiaryEntry(null);
        setFormData({ emotion_id: null, notes: '', photo_url: '' });
        setPhotoPreview(null);
      }
    } catch (error) {
      console.error('Failed to fetch diary entry:', error);
      setDiaryEntry(null);
      setFormData({ emotion_id: null, notes: '', photo_url: '' });
      setPhotoPreview(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDateClick = (date) => {
    setSelectedDate(date);
    fetchDiaryEntry(date);
    setShowDiaryModal(true);
  };

  const handlePhotoUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onloadend = () => {
      setPhotoPreview(reader.result);
    };
    reader.readAsDataURL(file);

    setUploadingPhoto(true);
    try {
      const formDataUpload = new FormData();
      formDataUpload.append('photo', file);
      const response = await api.post('/upload/photo', formDataUpload, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setFormData(prev => ({ ...prev, photo_url: response.data.photo_url }));
    } catch (error) {
      console.error('Failed to upload photo:', error);
      alert('사진 업로드에 실패했습니다.');
    } finally {
      setUploadingPhoto(false);
    }
  };

  const handleRemovePhoto = () => {
    setPhotoPreview(null);
    setFormData(prev => ({ ...prev, photo_url: '' }));
  };

  const handleSaveDiary = async () => {
    if (!formData.emotion_id) {
      alert('기분을 선택해주세요.');
      return;
    }

    try {
      await api.post('/emotions/record', {
        emotion_id: formData.emotion_id,
        date: format(selectedDate, 'yyyy-MM-dd'),
        notes: formData.notes,
        photo_url: formData.photo_url
      });
      setShowDiaryModal(false);
      fetchEmotionData();
    } catch (error) {
      console.error('Failed to save diary:', error);
      alert('저장에 실패했습니다.');
    }
  };

  const monthStart = startOfMonth(currentDate);
  const monthEnd = endOfMonth(currentDate);
  const calendarStart = startOfWeek(monthStart);
  const calendarEnd = endOfWeek(monthEnd);
  const days = eachDayOfInterval({ start: calendarStart, end: calendarEnd });

  const prevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1));
  };

  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1));
  };

  const getSelectedEmotion = () => {
    return emotions.find(e => e.id === formData.emotion_id);
  };

  return (
    <div className="calendar-page">
      <header className="page-header">
        <h1>기분 일기</h1>
        <p className="page-subtitle">날짜를 클릭하여 오늘의 기분과 사진을 기록하세요</p>
      </header>

      <div className="calendar-container card">
        <div className="calendar-nav">
          <button onClick={prevMonth} className="nav-btn">
            <ChevronLeft size={24} />
          </button>
          <h2>{format(currentDate, 'yyyy년 M월')}</h2>
          <button onClick={nextMonth} className="nav-btn">
            <ChevronRight size={24} />
          </button>
        </div>

        <div className="calendar-weekdays">
          {['일', '월', '화', '수', '목', '금', '토'].map(day => (
            <div key={day} className="weekday">{day}</div>
          ))}
        </div>

        <div className="calendar-grid full">
          {days.map(day => {
            const dateStr = format(day, 'yyyy-MM-dd');
            const emotion = emotionData[dateStr];

            return (
              <div
                key={dateStr}
                className={`calendar-day-full diary-mode ${!isSameMonth(day, currentDate) ? 'other-month' : ''} ${isToday(day) ? 'today' : ''} ${emotion ? 'has-emotion' : ''}`}
                onClick={() => handleDateClick(day)}
              >
                <div className="day-header">
                  <span className="day-number">{format(day, 'd')}</span>
                </div>
                {emotion && (
                  <div className="day-emotion-display" style={{ backgroundColor: emotion.color + '20' }}>
                    <span className="emotion-emoji-large">{emotion.emoji}</span>
                    {emotion.has_photo && <Camera size={12} className="photo-indicator" />}
                  </div>
                )}
                {!emotion && isSameMonth(day, currentDate) && (
                  <div className="day-empty">
                    <span className="add-diary-hint">+</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {showDiaryModal && selectedDate && (
        <div className="modal-overlay" onClick={() => setShowDiaryModal(false)}>
          <div className="modal diary-modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{format(selectedDate, 'yyyy년 M월 d일')} 기분 일기</h2>
              <button className="close-btn" onClick={() => setShowDiaryModal(false)}>
                <X size={20} />
              </button>
            </div>

            {isLoading ? (
              <div className="modal-loading">불러오는 중...</div>
            ) : (
              <div className="diary-content">
                <div className="diary-section">
                  <label className="section-label">오늘의 기분</label>
                  <div className="emotion-grid-diary">
                    {emotions.map((emotion) => (
                      <button
                        key={emotion.id}
                        className={`emotion-btn-diary ${formData.emotion_id === emotion.id ? 'selected' : ''}`}
                        style={{ 
                          backgroundColor: formData.emotion_id === emotion.id ? emotion.color : emotion.color + '30',
                          borderColor: emotion.color
                        }}
                        onClick={() => setFormData(prev => ({ ...prev, emotion_id: emotion.id }))}
                      >
                        <span className="emotion-emoji">{emotion.emoji}</span>
                        <span className="emotion-name">{emotion.name}</span>
                      </button>
                    ))}
                  </div>
                </div>

                <div className="diary-section">
                  <label className="section-label">오늘의 사진</label>
                  <div className="photo-upload-area">
                    {photoPreview ? (
                      <div className="photo-preview-container">
                        <img src={photoPreview} alt="Diary" className="photo-preview" />
                        <button className="remove-photo-btn" onClick={handleRemovePhoto}>
                          <Trash2 size={16} />
                        </button>
                      </div>
                    ) : (
                      <label className="photo-upload-box">
                        <input
                          type="file"
                          accept="image/*"
                          onChange={handlePhotoUpload}
                          style={{ display: 'none' }}
                        />
                        {uploadingPhoto ? (
                          <span>업로드 중...</span>
                        ) : (
                          <>
                            <Image size={32} />
                            <span>사진 추가하기</span>
                          </>
                        )}
                      </label>
                    )}
                  </div>
                </div>

                <div className="diary-section">
                  <label className="section-label">오늘의 일기</label>
                  <textarea
                    className="diary-notes"
                    placeholder="오늘 하루는 어땠나요? 기분을 자유롭게 적어보세요..."
                    value={formData.notes}
                    onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
                    rows={4}
                  />
                </div>

                <div className="modal-actions">
                  <button type="button" className="btn-secondary" onClick={() => setShowDiaryModal(false)}>
                    취소
                  </button>
                  <button 
                    type="button" 
                    className="btn-primary" 
                    onClick={handleSaveDiary}
                    disabled={!formData.emotion_id}
                  >
                    저장하기
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Calendar;
