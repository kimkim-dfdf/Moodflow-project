import { useState, useEffect } from 'react';
import { useDate } from '../context/DateContext';
import api from '../api/axios';
import TaskCard from '../components/TaskCard';
import MiniCalendar from '../components/MiniCalendar';
import { Sparkles, X, Calendar, RotateCcw } from 'lucide-react';
import { format, isToday } from 'date-fns';

function Tasks() {
  const { selectedDate, setSelectedDate } = useDate();
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedEmotion, setSelectedEmotion] = useState(null);
  const [suggestedTasks, setSuggestedTasks] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [showCalendar, setShowCalendar] = useState(false);

  useEffect(function() { fetchTasks(); fetchEmotion(); }, [selectedDate]);

  function fetchTasks() {
    api.get('/tasks', { params: { date: format(selectedDate, 'yyyy-MM-dd') } })
      .then(function(res) { setTasks(res.data); setLoading(false); });
  }

  function fetchEmotion() {
    api.get('/emotions/diary/' + format(selectedDate, 'yyyy-MM-dd'))
      .then(function(res) {
        if (res.data && res.data.emotion) setSelectedEmotion(res.data.emotion);
        else setSelectedEmotion(null);
      });
  }

  function handleToggle(task) {
    api.put('/tasks/' + task.id, { is_completed: !task.is_completed }).then(fetchTasks);
  }

  function handleDelete(task) {
    api.delete('/tasks/' + task.id).then(fetchTasks);
  }

  function handleGenerate() {
    if (!selectedEmotion) return;
    api.get('/tasks/suggestions', { params: { emotion: selectedEmotion.name, limit: 5 } })
      .then(function(res) { setSuggestedTasks(res.data); setShowSuggestions(true); });
  }

  function handleAdd(s) {
    api.post('/tasks', {
      title: s.title, category: s.category, priority: s.priority,
      task_date: format(selectedDate, 'yyyy-MM-dd'),
      recommended_for_emotion: selectedEmotion ? selectedEmotion.name : null
    }).then(fetchTasks);
  }

  var incomplete = [];
  var complete = [];
  for (var i = 0; i < tasks.length; i++) {
    if (tasks[i].is_completed) complete.push(tasks[i]);
    else incomplete.push(tasks[i]);
  }

  if (loading) return <div className="loading-screen">Loading...</div>;

  return (
    <div className="tasks-page">
      <header className="page-header">
        <div className="header-title-row">
          <h1>My Tasks</h1>
          <div className="date-selector">
            <button className="date-picker-btn" onClick={function() { setShowCalendar(!showCalendar); }}>
              <Calendar size={18} /> {format(selectedDate, 'MMM d, yyyy')}
            </button>
            {!isToday(selectedDate) && <button className="back-today-btn" onClick={function() { setSelectedDate(new Date()); }}><RotateCcw size={16} /> Today</button>}
          </div>
        </div>
        <button className="btn-primary" onClick={handleGenerate} disabled={!selectedEmotion}><Sparkles size={18} /> Generate Tasks</button>
      </header>

      {showCalendar && <div className="calendar-dropdown card"><MiniCalendar onDateSelect={function(d) { setSelectedDate(d); setShowCalendar(false); }} selectedDate={selectedDate} /></div>}

      {showSuggestions && suggestedTasks.length > 0 && (
        <div className="suggestions-panel card">
          <div className="panel-header">
            <h3>Suggested for {selectedEmotion ? selectedEmotion.name : ''}</h3>
            <button className="close-btn" onClick={function() { setShowSuggestions(false); }}><X size={18} /></button>
          </div>
          <div className="suggestions-list">
            {suggestedTasks.map(function(s, i) {
              return <div key={i} className="suggestion-item"><div className="suggestion-content"><p>{s.title}</p><span className="category-tag">{s.category}</span></div><button className="btn-small" onClick={function() { handleAdd(s); }}>Add</button></div>;
            })}
          </div>
        </div>
      )}

      <div className="tasks-content">
        <section className="tasks-section">
          <h2>To Do ({incomplete.length})</h2>
          {incomplete.length > 0 ? <div className="task-list">{incomplete.map(function(t) { return <TaskCard key={t.id} task={t} onToggle={handleToggle} onDelete={handleDelete} mode="tasks" />; })}</div> : <p className="empty-state">No tasks</p>}
        </section>
        <section className="tasks-section completed">
          <h2>Done ({complete.length})</h2>
          {complete.length > 0 ? <div className="task-list">{complete.map(function(t) { return <TaskCard key={t.id} task={t} onToggle={handleToggle} onDelete={handleDelete} mode="tasks" />; })}</div> : <p className="empty-state">No completed tasks</p>}
        </section>
      </div>
    </div>
  );
}

export default Tasks;
