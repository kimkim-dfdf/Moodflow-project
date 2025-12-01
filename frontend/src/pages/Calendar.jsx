import { useState, useEffect } from 'react';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isToday, startOfWeek, endOfWeek, isSameDay } from 'date-fns';
import { ChevronLeft, ChevronRight, Plus, X } from 'lucide-react';
import api from '../api/axios';

const Calendar = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [events, setEvents] = useState([]);
  const [emotionData, setEmotionData] = useState({});
  const [selectedDate, setSelectedDate] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingEvent, setEditingEvent] = useState(null);
  const [emotions, setEmotions] = useState([]);
  const [showEmotionModal, setShowEmotionModal] = useState(false);

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    start_date: '',
    end_date: '',
    all_day: true,
    color: '#6366f1'
  });

  useEffect(() => {
    fetchEvents();
    fetchEmotionData();
    fetchEmotions();
  }, [currentDate]);

  const fetchEvents = async () => {
    try {
      const response = await api.get('/calendar/events', {
        params: {
          month: currentDate.getMonth() + 1,
          year: currentDate.getFullYear()
        }
      });
      setEvents(response.data);
    } catch (error) {
      console.error('Failed to fetch events:', error);
    }
  };

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

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const eventData = {
        ...formData,
        start_date: new Date(formData.start_date).toISOString(),
        end_date: formData.end_date ? new Date(formData.end_date).toISOString() : null
      };

      if (editingEvent) {
        await api.put(`/calendar/events/${editingEvent.id}`, eventData);
      } else {
        await api.post('/calendar/events', eventData);
      }
      setShowModal(false);
      resetForm();
      fetchEvents();
    } catch (error) {
      console.error('Failed to save event:', error);
    }
  };

  const handleDelete = async (eventId) => {
    if (window.confirm('Are you sure you want to delete this event?')) {
      try {
        await api.delete(`/calendar/events/${eventId}`);
        fetchEvents();
      } catch (error) {
        console.error('Failed to delete event:', error);
      }
    }
  };

  const handleRecordEmotion = async (emotion) => {
    if (!selectedDate) return;
    try {
      await api.post('/emotions/record', {
        emotion_id: emotion.id,
        date: format(selectedDate, 'yyyy-MM-dd')
      });
      setShowEmotionModal(false);
      fetchEmotionData();
    } catch (error) {
      console.error('Failed to record emotion:', error);
    }
  };

  const resetForm = () => {
    setEditingEvent(null);
    setFormData({
      title: '',
      description: '',
      start_date: '',
      end_date: '',
      all_day: true,
      color: '#6366f1'
    });
  };

  const openNewEventModal = (date) => {
    resetForm();
    setFormData(prev => ({
      ...prev,
      start_date: format(date, "yyyy-MM-dd'T'HH:mm")
    }));
    setShowModal(true);
  };

  const openEditEventModal = (event) => {
    setEditingEvent(event);
    setFormData({
      title: event.title,
      description: event.description || '',
      start_date: event.start_date.slice(0, 16),
      end_date: event.end_date ? event.end_date.slice(0, 16) : '',
      all_day: event.all_day,
      color: event.color
    });
    setShowModal(true);
  };

  const monthStart = startOfMonth(currentDate);
  const monthEnd = endOfMonth(currentDate);
  const calendarStart = startOfWeek(monthStart);
  const calendarEnd = endOfWeek(monthEnd);
  const days = eachDayOfInterval({ start: calendarStart, end: calendarEnd });

  const getEventsForDay = (day) => {
    return events.filter(event => {
      const eventDate = new Date(event.start_date);
      return isSameDay(eventDate, day);
    });
  };

  const prevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1));
  };

  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1));
  };

  return (
    <div className="calendar-page">
      <header className="page-header">
        <h1>Calendar</h1>
        <button className="btn-primary" onClick={() => openNewEventModal(new Date())}>
          <Plus size={18} />
          Add Event
        </button>
      </header>

      <div className="calendar-container card">
        <div className="calendar-nav">
          <button onClick={prevMonth} className="nav-btn">
            <ChevronLeft size={24} />
          </button>
          <h2>{format(currentDate, 'MMMM yyyy')}</h2>
          <button onClick={nextMonth} className="nav-btn">
            <ChevronRight size={24} />
          </button>
        </div>

        <div className="calendar-weekdays">
          {['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'].map(day => (
            <div key={day} className="weekday">{day}</div>
          ))}
        </div>

        <div className="calendar-grid full">
          {days.map(day => {
            const dateStr = format(day, 'yyyy-MM-dd');
            const emotion = emotionData[dateStr];
            const dayEvents = getEventsForDay(day);

            return (
              <div
                key={dateStr}
                className={`calendar-day-full ${!isSameMonth(day, currentDate) ? 'other-month' : ''} ${isToday(day) ? 'today' : ''}`}
                onClick={() => {
                  setSelectedDate(day);
                }}
              >
                <div className="day-header">
                  <span className="day-number">{format(day, 'd')}</span>
                  {emotion && (
                    <span 
                      className="day-emotion-badge" 
                      style={{ backgroundColor: emotion.color }}
                      title={emotion.emotion}
                    >
                      {emotion.emoji}
                    </span>
                  )}
                  <button
                    className="record-emotion-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedDate(day);
                      setShowEmotionModal(true);
                    }}
                    title="Record emotion for this day"
                  >
                    {emotion ? 'Change' : '+'}
                  </button>
                </div>
                <div className="day-events">
                  {dayEvents.slice(0, 3).map(event => (
                    <div
                      key={event.id}
                      className="event-pill"
                      style={{ backgroundColor: event.color }}
                      onClick={(e) => {
                        e.stopPropagation();
                        openEditEventModal(event);
                      }}
                    >
                      {event.title}
                    </div>
                  ))}
                  {dayEvents.length > 3 && (
                    <span className="more-events">+{dayEvents.length - 3} more</span>
                  )}
                </div>
                <button
                  className="add-event-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    openNewEventModal(day);
                  }}
                >
                  +
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingEvent ? 'Edit Event' : 'New Event'}</h2>
              <button className="close-btn" onClick={() => setShowModal(false)}>
                <X size={20} />
              </button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="title">Title</label>
                <input
                  type="text"
                  id="title"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="Event title"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="description">Description</label>
                <textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Event description (optional)"
                  rows={3}
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="start_date">Start Date & Time</label>
                  <input
                    type="datetime-local"
                    id="start_date"
                    value={formData.start_date}
                    onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="end_date">End Date & Time</label>
                  <input
                    type="datetime-local"
                    id="end_date"
                    value={formData.end_date}
                    onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group checkbox-group">
                  <input
                    type="checkbox"
                    id="all_day"
                    checked={formData.all_day}
                    onChange={(e) => setFormData({ ...formData, all_day: e.target.checked })}
                  />
                  <label htmlFor="all_day">All day event</label>
                </div>

                <div className="form-group">
                  <label htmlFor="color">Color</label>
                  <input
                    type="color"
                    id="color"
                    value={formData.color}
                    onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                  />
                </div>
              </div>

              <div className="modal-actions">
                {editingEvent && (
                  <button 
                    type="button" 
                    className="btn-danger" 
                    onClick={() => {
                      handleDelete(editingEvent.id);
                      setShowModal(false);
                    }}
                  >
                    Delete
                  </button>
                )}
                <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  {editingEvent ? 'Update Event' : 'Create Event'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showEmotionModal && (
        <div className="modal-overlay" onClick={() => setShowEmotionModal(false)}>
          <div className="modal emotion-modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>How did you feel on {selectedDate && format(selectedDate, 'MMMM d, yyyy')}?</h2>
              <button className="close-btn" onClick={() => setShowEmotionModal(false)}>
                <X size={20} />
              </button>
            </div>
            <div className="emotion-grid-modal">
              {emotions.map((emotion) => (
                <button
                  key={emotion.id}
                  className="emotion-btn-large"
                  style={{ backgroundColor: emotion.color }}
                  onClick={() => handleRecordEmotion(emotion)}
                >
                  <span className="emotion-emoji">{emotion.emoji}</span>
                  <span className="emotion-name">{emotion.name}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Calendar;
