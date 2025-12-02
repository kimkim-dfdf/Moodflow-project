import { useState, useEffect } from 'react';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isToday, isSameDay, startOfWeek, endOfWeek } from 'date-fns';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import api from '../api/axios';

function MiniCalendar({ onDateSelect, selectedDate }) {
  const [currentDate, setCurrentDate] = useState(selectedDate || new Date());
  const [emotionData, setEmotionData] = useState({});

  useEffect(() => {
    api.get('/emotions/statistics', { params: { days: 30 } })
      .then(response => {
        setEmotionData(response.data.daily_emotions || {});
      })
      .catch(error => {
        console.error('Failed to fetch emotion data:', error);
      });
  }, [currentDate]);

  const today = new Date();
  
  function isFutureDate(date) {
    const todayStart = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    const dateStart = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    return dateStart > todayStart;
  }

  function isCurrentMonth() {
    return currentDate.getMonth() === today.getMonth() && 
           currentDate.getFullYear() === today.getFullYear();
  }

  function goToPrevMonth() {
    const newDate = new Date(currentDate.getFullYear(), currentDate.getMonth() - 1);
    setCurrentDate(newDate);
  }

  function goToNextMonth() {
    if (!isCurrentMonth()) {
      const newDate = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1);
      setCurrentDate(newDate);
    }
  }

  function handleDayClick(day) {
    if (!isFutureDate(day) && onDateSelect) {
      onDateSelect(day);
    }
  }

  function getDayClassName(day) {
    let className = 'calendar-day';
    
    if (!isSameMonth(day, currentDate)) {
      className = className + ' other-month';
    }
    if (isToday(day)) {
      className = className + ' today';
    }
    if (selectedDate && isSameDay(day, selectedDate)) {
      className = className + ' selected';
    }
    if (isFutureDate(day)) {
      className = className + ' future-date';
    }
    
    return className;
  }

  const monthStart = startOfMonth(currentDate);
  const monthEnd = endOfMonth(currentDate);
  const calendarStart = startOfWeek(monthStart);
  const calendarEnd = endOfWeek(monthEnd);
  const days = eachDayOfInterval({ start: calendarStart, end: calendarEnd });
  const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  return (
    <div className="mini-calendar">
      <div className="calendar-header">
        <button onClick={goToPrevMonth} className="nav-btn">
          <ChevronLeft size={18} />
        </button>
        <h3>{format(currentDate, 'MMMM yyyy')}</h3>
        <button 
          onClick={goToNextMonth} 
          className={isCurrentMonth() ? 'nav-btn disabled' : 'nav-btn'}
          disabled={isCurrentMonth()}
        >
          <ChevronRight size={18} />
        </button>
      </div>

      <div className="calendar-weekdays">
        {weekdays.map(function(day) {
          return <div key={day} className="weekday">{day}</div>;
        })}
      </div>

      <div className="calendar-grid">
        {days.map(function(day) {
          const dateStr = format(day, 'yyyy-MM-dd');
          const emotion = emotionData[dateStr];
          const isFuture = isFutureDate(day);
          
          let style = {};
          if (isFuture) {
            style = { cursor: 'not-allowed' };
          } else if (emotion) {
            style = { backgroundColor: emotion.color + '20' };
          }

          return (
            <div
              key={dateStr}
              className={getDayClassName(day)}
              onClick={function() { handleDayClick(day); }}
              style={style}
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
}

export default MiniCalendar;
