import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isToday, startOfWeek, endOfWeek } from 'date-fns';
import { ChevronLeft, ChevronRight, X, Camera, Image, Trash2 } from 'lucide-react';
import api from '../api/axios';

function Calendar() {
  const navigate = useNavigate();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [emotionData, setEmotionData] = useState({});
  const [selectedDate, setSelectedDate] = useState(null);
  const [emotions, setEmotions] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({ emotion_id: null, notes: '', photo_url: '' });
  const [photoPreview, setPhotoPreview] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [showAnalysis, setShowAnalysis] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);

  useEffect(function() {
    fetchData();
  }, [currentDate]);

  function fetchData() {
    api.get('/emotions/statistics', { params: { days: 60 } }).then(function(res) {
      setEmotionData(res.data.daily_emotions || {});
    });
    api.get('/emotions').then(function(res) {
      setEmotions(res.data);
    });
  }

  function handleDateClick(date) {
    var todayStart = new Date();
    todayStart.setHours(0, 0, 0, 0);
    if (date > todayStart) return;
    
    setSelectedDate(date);
    setIsLoading(true);
    
    var dateStr = format(date, 'yyyy-MM-dd');
    api.get('/emotions/diary/' + dateStr).then(function(res) {
      if (res.data) {
        setFormData({ emotion_id: res.data.emotion_id, notes: res.data.notes || '', photo_url: res.data.photo_url || '' });
        if (res.data.photo_url) {
          setPhotoPreview(window.location.origin + res.data.photo_url);
        } else {
          setPhotoPreview(null);
        }
      } else {
        setFormData({ emotion_id: null, notes: '', photo_url: '' });
        setPhotoPreview(null);
      }
      setIsLoading(false);
      setShowModal(true);
    });
  }

  function handlePhotoUpload(e) {
    var file = e.target.files[0];
    if (!file) return;
    
    var reader = new FileReader();
    reader.onloadend = function() { setPhotoPreview(reader.result); };
    reader.readAsDataURL(file);
    
    setUploading(true);
    var fd = new FormData();
    fd.append('photo', file);
    api.post('/upload/photo', fd, { headers: { 'Content-Type': 'multipart/form-data' } }).then(function(res) {
      setFormData({ ...formData, photo_url: res.data.photo_url });
      setUploading(false);
    }).catch(function() {
      alert('Upload failed');
      setUploading(false);
    });
  }

  function handleSave() {
    if (!formData.emotion_id) {
      alert('Please select a mood');
      return;
    }
    api.post('/emotions/record', {
      emotion_id: formData.emotion_id,
      date: format(selectedDate, 'yyyy-MM-dd'),
      notes: formData.notes,
      photo_url: formData.photo_url
    }).then(function() {
      setShowModal(false);
      fetchData();
    });
  }

  function toggleAnalysis() {
    if (showAnalysis) {
      setShowAnalysis(false);
    } else {
      setAnalysisLoading(true);
      api.get('/ai/monthly-analysis').then(function(res) {
        setAnalysis(res.data);
        setShowAnalysis(true);
        setAnalysisLoading(false);
      }).catch(function() {
        alert('Failed to load analysis');
        setAnalysisLoading(false);
      });
    }
  }

  var monthStart = startOfMonth(currentDate);
  var monthEnd = endOfMonth(currentDate);
  var days = eachDayOfInterval({ start: startOfWeek(monthStart), end: endOfWeek(monthEnd) });
  var today = new Date();
  var isCurrentMonth = currentDate.getMonth() === today.getMonth() && currentDate.getFullYear() === today.getFullYear();

  function isFuture(date) {
    var todayStart = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    return date > todayStart;
  }

  return (

    <div className="calendar-page">
      <header className="page-header" style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 24 }}>
          <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <h1 style={{ margin: 0, fontSize: 32, fontWeight: 700 }}>Emotion Diary</h1>
            <span style={{ fontSize: 15, color: '#888', marginTop: 4, fontWeight: 400 }}>Click a date to record your mood and notes</span>
          </div>
        </div>
      </header>

      <div className="calendar-container card">
        <div className="calendar-nav">
          <button onClick={function() { setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1)); }} className="nav-btn"><ChevronLeft size={24} /></button>
          <h2>{format(currentDate, 'MMMM yyyy')}</h2>
          <button onClick={function() { if (!isCurrentMonth) setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1)); }} className={'nav-btn ' + (isCurrentMonth ? 'disabled' : '')} disabled={isCurrentMonth}><ChevronRight size={24} /></button>
        </div>

        <div style={{ marginBottom: 16 }}>
          <button onClick={toggleAnalysis} className="btn-analysis" style={{ width: '100%', padding: '12px 16px', backgroundColor: '#f0e8ff', color: '#5b6ee1', border: 'none', borderRadius: 8, fontWeight: 600, cursor: 'pointer', fontSize: 15, transition: 'all 0.2s' }}>
            {showAnalysis ? 'Hide Monthly Analysis' : 'View AI Monthly Analysis'}
          </button>
        </div>

        {showAnalysis && (
          <div className="analysis-section" style={{ backgroundColor: '#faf9ff', border: '1px solid #e8e0ff', borderRadius: 8, padding: 20, marginBottom: 16 }}>
            {analysisLoading ? (
              <div style={{ textAlign: 'center', padding: 20, color: '#999' }}>Loading analysis...</div>
            ) : analysis ? (
              <div>
                <h3 style={{ margin: '0 0 12px 0', fontSize: 16, fontWeight: 600, color: '#5b6ee1' }}>AI Monthly Summary</h3>
                <p style={{ fontSize: 14, color: '#555', lineHeight: 1.6, marginBottom: 20, fontWeight: 400 }}>{analysis.summary}</p>
                
                {analysis.keywords && analysis.keywords.length > 0 && (
                  <div style={{ marginBottom: 16 }}>
                    <h4 style={{ margin: '0 0 8px 0', fontSize: 13, fontWeight: 600, color: '#888', textTransform: 'uppercase' }}>Top Keywords</h4>
                    <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                      {analysis.keywords.map(function(kw, idx) {
                        return (
                          <span key={idx} style={{ backgroundColor: '#e8e0ff', color: '#5b6ee1', padding: '6px 12px', borderRadius: 20, fontSize: 12, fontWeight: 500 }}>
                            {kw}
                          </span>
                        );
                      })}
                    </div>
                  </div>
                )}
                
                <div style={{ padding: '12px 16px', backgroundColor: '#f0e8ff', borderRadius: 8, borderLeft: '3px solid #5b6ee1' }}>
                  <p style={{ margin: 0, fontSize: 13, color: '#555', lineHeight: 1.5, fontStyle: 'italic' }}>💭 {analysis.next_month_message}</p>
                </div>
              </div>
            ) : null}
          </div>
        )}

        <div className="calendar-weekdays">
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(function(d) { return <div key={d} className="weekday">{d}</div>; })}
        </div>

        <div className="calendar-grid full">
          {days.map(function(day) {
            var dateStr = format(day, 'yyyy-MM-dd');
            var emotion = emotionData[dateStr];
            var future = isFuture(day);
            var classes = 'calendar-day-full diary-mode';
            if (!isSameMonth(day, currentDate)) classes += ' other-month';
            if (isToday(day)) classes += ' today';
            if (emotion) classes += ' has-emotion';
            if (future) classes += ' future-date';

            return (
              <div key={dateStr} className={classes} onClick={function() { if (!future) handleDateClick(day); }}>
                <div className="day-header"><span className="day-number">{format(day, 'd')}</span></div>
                {emotion && (
                  <div className="day-emotion-display" style={{ backgroundColor: emotion.color + '20' }}>
                    <span className="day-emotion-large">{emotion.emoji}</span>
                    {emotion.has_photo && <Camera size={12} className="photo-indicator" />}
                  </div>
                )}
                {!emotion && isSameMonth(day, currentDate) && !future && <div className="day-empty"><span>+</span></div>}
              </div>
            );
          })}
        </div>
      </div>

      {showModal && selectedDate && (
        <div className="modal-overlay" onClick={function() { setShowModal(false); }}>
          <div className="modal diary-modal" onClick={function(e) { e.stopPropagation(); }}>
            <div className="modal-header">
              <h2>Emotion Diary - {format(selectedDate, 'MMM d, yyyy')}</h2>
              <button className="close-btn" onClick={function() { setShowModal(false); }}><X size={20} /></button>
            </div>

            {isLoading ? <div style={{ padding: 24 }}>Loading...</div> : (
              <div className="diary-content">
                <div className="diary-section">
                  <label className="section-label">Mood</label>
                  <div className="emotion-grid-diary">
                    {emotions.map(function(em) {
                      var selected = formData.emotion_id === em.id;
                      return (
                        <button key={em.id} className={'emotion-btn-diary ' + (selected ? 'selected' : '')} style={{ backgroundColor: selected ? em.color : em.color + '30', borderColor: em.color }} onClick={function() { setFormData({ ...formData, emotion_id: em.id }); }}>
                          <span className="emotion-emoji">{em.emoji}</span>
                          <span className="emotion-name">{em.name}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>

                <div className="diary-section">
                  <label className="section-label">Photo</label>
                  <div className="photo-upload-area">
                    {photoPreview ? (
                      <div className="photo-preview-container">
                        <img src={photoPreview} alt="Diary" className="photo-preview" />
                        <button className="remove-photo-btn" onClick={function() { setPhotoPreview(null); setFormData({ ...formData, photo_url: '' }); }}><Trash2 size={16} /></button>
                      </div>
                    ) : (
                      <label className="photo-upload-box">
                        <input type="file" accept="image/*" onChange={handlePhotoUpload} style={{ display: 'none' }} />
                        {uploading ? <span>Uploading...</span> : <><Image size={32} /><span>Add Photo</span></>}
                      </label>
                    )}
                  </div>
                </div>

                <div className="diary-section">
                  <label className="section-label">Notes</label>
                  <textarea className="diary-notes" placeholder="Write about your day, thoughts, or feelings..." value={formData.notes} onChange={function(e) { setFormData({ ...formData, notes: e.target.value }); }} rows={4} />
                </div>

                <div className="modal-actions">
                  <button className="btn-secondary" onClick={function() { setShowModal(false); }}>Cancel</button>
                  <button className="btn-primary" onClick={handleSave} disabled={!formData.emotion_id}>Save</button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default Calendar;
