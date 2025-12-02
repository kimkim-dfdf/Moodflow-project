import { useState, useEffect } from 'react';
import { format, startOfMonth, endOfMonth, startOfWeek, endOfWeek, addDays, isSameMonth, isSameDay, addMonths, subMonths } from 'date-fns';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import api from '../api/axios';

function MiniCalendar({ onDateSelect, selectedDate }) {
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [emotionData, setEmotionData] = useState({});

  useEffect(function() {
    fetchMonthEmotions();
  }, [currentMonth]);

  function fetchMonthEmotions() {
    api.get('/emotions/statistics', { params: { days: 60 } })
      .then(function(response) {
        if (response.data && response.data.daily_emotions) {
          setEmotionData(response.data.daily_emotions);
        }
      })
      .catch(function(error) {
        console.error('Failed to fetch emotions:', error);
      });
  }

  function handlePrevMonth() {
    setCurrentMonth(subMonths(currentMonth, 1));
  }

  function handleNextMonth() {
    setCurrentMonth(addMonths(currentMonth, 1));
  }

  function handleDateClick(day) {
    if (onDateSelect) {
      onDateSelect(day);
    }
  }

  function renderHeader() {
    return (
      <div className="calendar-header">
        <button className="nav-btn" onClick={handlePrevMonth}>
          <ChevronLeft size={18} />
        </button>
        <span className="current-month">{format(currentMonth, 'MMMM yyyy')}</span>
        <button className="nav-btn" onClick={handleNextMonth}>
          <ChevronRight size={18} />
        </button>
      </div>
    );
  }

  function renderDays() {
    var days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    var dayElements = [];
    
    for (var i = 0; i < days.length; i++) {
      dayElements.push(
        <div className="day-name" key={days[i]}>
          {days[i]}
        </div>
      );
    }
    
    return <div className="days-row">{dayElements}</div>;
  }

  function renderCells() {
    var monthStart = startOfMonth(currentMonth);
    var monthEnd = endOfMonth(monthStart);
    var startDate = startOfWeek(monthStart);
    var endDate = endOfWeek(monthEnd);

    var rows = [];
    var days = [];
    var day = startDate;

    while (day <= endDate) {
      for (var i = 0; i < 7; i++) {
        var dateStr = format(day, 'yyyy-MM-dd');
        var dayData = emotionData[dateStr];
        var isCurrentMonth = isSameMonth(day, monthStart);
        var isSelected = isSameDay(day, selectedDate);
        var isToday = isSameDay(day, new Date());

        var className = 'calendar-cell';
        if (!isCurrentMonth) {
          className = className + ' other-month';
        }
        if (isSelected) {
          className = className + ' selected';
        }
        if (isToday) {
          className = className + ' today';
        }
        if (dayData) {
          className = className + ' has-emotion';
        }

        var cellStyle = {};
        if (dayData && dayData.color) {
          cellStyle = { borderBottom: '3px solid ' + dayData.color };
        }

        var dayNumber = format(day, 'd');
        var currentDay = day;

        days.push(
          <div
            className={className}
            key={dateStr}
            style={cellStyle}
            onClick={function(d) {
              return function() { handleDateClick(d); };
            }(currentDay)}
          >
            <span className="day-number">{dayNumber}</span>
            {dayData && dayData.emoji && (
              <span className="day-emoji">{dayData.emoji}</span>
            )}
          </div>
        );

        day = addDays(day, 1);
      }

      rows.push(
        <div className="calendar-row" key={day.toString()}>
          {days}
        </div>
      );
      days = [];
    }

    return <div className="calendar-body">{rows}</div>;
  }

  return (
    <div className="mini-calendar">
      {renderHeader()}
      {renderDays()}
      {renderCells()}
    </div>
  );
}

export default MiniCalendar;
