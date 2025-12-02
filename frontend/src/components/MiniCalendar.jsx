import { useState, useEffect } from 'react';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isToday, isSameDay, startOfWeek, endOfWeek } from 'date-fns';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import api from '../api/axios';

function MiniCalendar(props) {
  var onDateSelect = props.onDateSelect;
  var selectedDate = props.selectedDate;
  
  const [currentDate, setCurrentDate] = useState(selectedDate || new Date());
  const [emotionData, setEmotionData] = useState({});
  var today = new Date();

  useEffect(function() {
    api.get('/emotions/statistics', { params: { days: 30 } }).then(function(res) {
      setEmotionData(res.data.daily_emotions || {});
    });
  }, [currentDate]);

  function isFutureDate(date) {
    var todayStart = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    var dateStart = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    return dateStart > todayStart;
  }

  function isCurrentMonth() {
    return currentDate.getMonth() === today.getMonth() && currentDate.getFullYear() === today.getFullYear();
  }

  function goToPrevMonth() {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1));
  }

  function goToNextMonth() {
    if (!isCurrentMonth()) {
      setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1));
    }
  }

  function handleDayClick(day) {
    if (!isFutureDate(day) && onDateSelect) {
      onDateSelect(day);
    }
  }

  function getDayClassName(day) {
    var className = 'calendar-day';
    if (!isSameMonth(day, currentDate)) className += ' other-month';
    if (isToday(day)) className += ' today';
    if (selectedDate && isSameDay(day, selectedDate)) className += ' selected';
    if (isFutureDate(day)) className += ' future-date';
    return className;
  }

  var monthStart = startOfMonth(currentDate);
  var monthEnd = endOfMonth(currentDate);
  var days = eachDayOfInterval({ start: startOfWeek(monthStart), end: endOfWeek(monthEnd) });
  var weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  return (
    <div className="mini-calendar">
      <div className="calendar-header">
        <button onClick={goToPrevMonth} className="nav-btn"><ChevronLeft size={18} /></button>
        <h3>{format(currentDate, 'MMMM yyyy')}</h3>
        <button onClick={goToNextMonth} className={'nav-btn ' + (isCurrentMonth() ? 'disabled' : '')} disabled={isCurrentMonth()}><ChevronRight size={18} /></button>
      </div>

      <div className="calendar-weekdays">
        {weekdays.map(function(d) { return <div key={d} className="weekday">{d}</div>; })}
      </div>

      <div className="calendar-grid">
        {days.map(function(day) {
          var dateStr = format(day, 'yyyy-MM-dd');
          var emotion = emotionData[dateStr];
          var isFuture = isFutureDate(day);
          var style = {};
          if (isFuture) style = { cursor: 'not-allowed' };
          else if (emotion) style = { backgroundColor: emotion.color + '20' };

          return (
            <div key={dateStr} className={getDayClassName(day)} onClick={function() { handleDayClick(day); }} style={style}>
              <span className="day-number">{format(day, 'd')}</span>
              {emotion && <span className="day-emotion" title={emotion.emotion}>{emotion.emoji}</span>}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default MiniCalendar;
