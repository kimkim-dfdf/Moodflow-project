import { useState, useEffect } from 'react';
import { useDate } from '../context/DateContext';
import api from '../api/axios';
import TaskCard from '../components/TaskCard';
import MiniCalendar from '../components/MiniCalendar';
import { Sparkles, X, Calendar, RotateCcw } from 'lucide-react';
import { format, isToday } from 'date-fns';

const Tasks = () => {
  const { selectedDate, setSelectedDate } = useDate();

  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedEmotion, setSelectedEmotion] = useState(null);
  const [suggestedTasks, setSuggestedTasks] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [showCalendar, setShowCalendar] = useState(false);

  useEffect(() => {
    fetchTasks();
    fetchDateEmotion();
  }, [selectedDate]);

  const fetchTasks = async () => {
    try {
      const params = { date: format(selectedDate, 'yyyy-MM-dd') };
      const response = await api.get('/tasks', { params });
      setTasks(response.data);
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchDateEmotion = async () => {
    try {
      const dateStr = format(selectedDate, 'yyyy-MM-dd');
      const response = await api.get(`/emotions/diary/${dateStr}`);
      if (response.data && response.data.emotion) {
        setSelectedEmotion(response.data.emotion);
      } else {
        setSelectedEmotion(null);
      }
    } catch (error) {
      console.error('Failed to fetch date emotion:', error);
      setSelectedEmotion(null);
    }
  };

  const fetchSuggestions = async (emotionName) => {
    try {
      const response = await api.get('/tasks/suggestions', {
        params: { emotion: emotionName, limit: 5 }
      });
      setSuggestedTasks(response.data);
      setShowSuggestions(true);
    } catch (error) {
      console.error('Failed to fetch suggestions:', error);
    }
  };

  const handleToggle = async (task) => {
    try {
      await api.put(`/tasks/${task.id}`, { is_completed: !task.is_completed });
      fetchTasks();
    } catch (error) {
      console.error('Failed to toggle task:', error);
    }
  };

  const handleAddSuggestion = async (suggestion) => {
    try {
      await api.post('/tasks', {
        title: suggestion.title,
        category: suggestion.category,
        priority: suggestion.priority,
        task_date: format(selectedDate, 'yyyy-MM-dd'),
        recommended_for_emotion: selectedEmotion?.name
      });
      fetchTasks();
    } catch (error) {
      console.error('Failed to add suggestion:', error);
    }
  };

  const handleDateSelect = (date) => {
    setSelectedDate(date);
    setShowCalendar(false);
    setLoading(true);
  };

  const handleBackToToday = () => {
    setSelectedDate(new Date());
    setLoading(true);
  };

  const incompleteTasks = tasks.filter(t => !t.is_completed);
  const completedTasks = tasks.filter(t => t.is_completed);

  if (loading) {
    return <div className="loading-screen">Loading tasks...</div>;
  }

  return (
    <div className="tasks-page">
      <header className="page-header">
        <div className="header-title-row">
          <h1>My Tasks</h1>
          <div className="date-selector">
            <button 
              className="date-picker-btn"
              onClick={() => setShowCalendar(!showCalendar)}
            >
              <Calendar size={18} />
              {format(selectedDate, 'MMM d, yyyy')}
            </button>
            {!isToday(selectedDate) && (
              <button className="back-today-btn" onClick={handleBackToToday}>
                <RotateCcw size={16} />
                Back to Today
              </button>
            )}
          </div>
        </div>
        <div className="header-actions">
          <button 
            className="btn-primary"
            onClick={() => selectedEmotion && fetchSuggestions(selectedEmotion.name)}
            disabled={!selectedEmotion}
          >
            <Sparkles size={18} />
            Generate Emotion Tasks
          </button>
        </div>
      </header>

      {showCalendar && (
        <div className="calendar-dropdown card">
          <MiniCalendar 
            onDateSelect={handleDateSelect}
            selectedDate={selectedDate}
          />
        </div>
      )}


      {showSuggestions && suggestedTasks.length > 0 && (
        <div className="suggestions-panel card">
          <div className="panel-header">
            <h3>Suggested Tasks for {selectedEmotion?.name} Mood</h3>
            <button className="close-btn" onClick={() => setShowSuggestions(false)}>
              <X size={18} />
            </button>
          </div>
          <div className="suggestions-list">
            {suggestedTasks.map((suggestion, index) => (
              <div key={index} className="suggestion-item">
                <div className="suggestion-content">
                  <p>{suggestion.title}</p>
                  <span className="category-tag">{suggestion.category}</span>
                </div>
                <button 
                  className="btn-small"
                  onClick={() => handleAddSuggestion(suggestion)}
                >
                  Add
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="tasks-content">
        <section className="tasks-section">
          <h2>To Do ({incompleteTasks.length})</h2>
          {incompleteTasks.length > 0 ? (
            <div className="task-list">
              {incompleteTasks.map((task) => (
                <TaskCard key={task.id} task={task} onToggle={handleToggle} mode="tasks" />
              ))}
            </div>
          ) : (
            <p className="empty-state">No pending tasks for this date.</p>
          )}
        </section>

        <section className="tasks-section completed">
          <h2>Completed ({completedTasks.length})</h2>
          {completedTasks.length > 0 ? (
            <div className="task-list">
              {completedTasks.map((task) => (
                <TaskCard key={task.id} task={task} onToggle={handleToggle} mode="tasks" />
              ))}
            </div>
          ) : (
            <p className="empty-state">No completed tasks for this date.</p>
          )}
        </section>
      </div>
    </div>
  );
};

export default Tasks;
