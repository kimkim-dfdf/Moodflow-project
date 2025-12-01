import { useState, useEffect } from 'react';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isToday, isSameDay, startOfWeek, endOfWeek, isFuture } from 'date-fns';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import api from '../api/axios';

const MiniCalendar = ({ onDateSelect, selectedDate }) => {
  const [currentDate, setCurrentDate] = useState(new Date());
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

  const prevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1));
  };

  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1));
  };

  return (
    <div className="mini-calendar">
      <div className="calendar-header">
        <button onClick={prevMonth} className="nav-btn">
          <ChevronLeft size={18} />
        </button>
        <h3>{format(currentDate, 'MMMM yyyy')}</h3>
        <button onClick={nextMonth} className="nav-btn">
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
          const isSelected = selectedDate && isSameDay(day, selectedDate);
          const isFutureDate = isFuture(day) && !isToday(day);
          
          return (
            <div
              key={dateStr}
              className={`calendar-day ${!isSameMonth(day, currentDate) ? 'other-month' : ''} ${isToday(day) ? 'today' : ''} ${isSelected ? 'selected' : ''} ${isFutureDate ? 'future-disabled' : ''}`}
              onClick={() => !isFutureDate && onDateSelect && onDateSelect(day)}
              style={emotion ? { backgroundColor: `${emotion.color}20` } : {}}
            >
              <span className="day-number">{format(day, 'd')}</span>
              {emotion && (
                <span className="day-emotion" title={emotion.emotion}>
                  {emotion.emoji}
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
