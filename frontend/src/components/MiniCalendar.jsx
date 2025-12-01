import { useState, useEffect } from 'react';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isToday, isSameDay, startOfWeek, endOfWeek } from 'date-fns';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import api from '../api/axios';
import SeedIcon from './SeedIcon';

const MiniCalendar = ({ onDateSelect, selectedDate }) => {
  const [currentDate, setCurrentDate] = useState(selectedDate || new Date());
  const [emotionData, setEmotionData] = useState({});

  useEffect(() => {
    fetchEmotionData();
  }, [currentDate]);

  const fetchEmotionData = async () => {
    try {
      const response = await api.get('/emotions/statistics', {
        params: { days: 30 }
      });
      setEmotionData(response.data.daily_emotions || {});
    } catch (error) {
      console.error('Failed to fetch emotion data:', error);
    }
  };

  const monthStart = startOfMonth(currentDate);
  const monthEnd = endOfMonth(currentDate);
  const calendarStart = startOfWeek(monthStart);
  const calendarEnd = endOfWeek(monthEnd);
  const days = eachDayOfInterval({ start: calendarStart, end: calendarEnd });

  const today = new Date();
  const isCurrentMonth = currentDate.getMonth() === today.getMonth() && currentDate.getFullYear() === today.getFullYear();

  const isFutureDate = (date) => {
    const todayStart = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    const dateStart = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    return dateStart > todayStart;
  };

  const prevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1));
  };

  const nextMonth = () => {
    if (!isCurrentMonth) {
      setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1));
    }
  };

  return (
    <div className="mini-calendar">
      <div className="calendar-header">
        <button onClick={prevMonth} className="nav-btn">
          <ChevronLeft size={18} />
        </button>
        <h3>{format(currentDate, 'MMMM yyyy')}</h3>
        <button 
          onClick={nextMonth} 
          className={`nav-btn ${isCurrentMonth ? 'disabled' : ''}`}
          disabled={isCurrentMonth}
        >
          <ChevronRight size={18} />
        </button>
      </div>

      <div className="calendar-weekdays">
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
          <div key={day} className="weekday">{day}</div>
        ))}
      </div>

      <div className="calendar-grid">
        {days.map(day => {
          const dateStr = format(day, 'yyyy-MM-dd');
          const emotion = emotionData[dateStr];
          const isFuture = isFutureDate(day);
          
          return (
            <div
              key={dateStr}
              className={`calendar-day ${!isSameMonth(day, currentDate) ? 'other-month' : ''} ${isToday(day) ? 'today' : ''} ${selectedDate && isSameDay(day, selectedDate) ? 'selected' : ''} ${isFuture ? 'future-date' : ''}`}
              onClick={() => !isFuture && onDateSelect && onDateSelect(day)}
              style={isFuture ? { cursor: 'not-allowed' } : (emotion ? { backgroundColor: `${emotion.color}20` } : {})}
            >
              <span className="day-number">{format(day, 'd')}</span>
              {emotion && (
                <span className="day-emotion" title={emotion.emotion}>
                  <SeedIcon color={emotion.color} size={12} />
                </span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default MiniCalendar;
