import { useState, useEffect } from 'react';
import { useDate } from '../context/DateContext';
import api from '../api/axios';
import TaskCard from '../components/TaskCard';
import { Sparkles, X } from 'lucide-react';
import { format } from 'date-fns';

function Tasks() {
  const { selectedDate } = useDate();
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedEmotion, setSelectedEmotion] = useState(null);
  const [suggestedTasks, setSuggestedTasks] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  useEffect(function() {
    fetchTasks();
    fetchDateEmotion();
  }, [selectedDate]);

  function fetchTasks() {
    var dateStr = format(selectedDate, 'yyyy-MM-dd');
    
    api.get('/tasks', { params: { date: dateStr } })
      .then(function(response) {
        setTasks(response.data);
        setLoading(false);
      })
      .catch(function(error) {
        console.error('Failed to fetch tasks:', error);
        setLoading(false);
      });
  }

  function fetchDateEmotion() {
    var dateStr = format(selectedDate, 'yyyy-MM-dd');
    
    api.get('/emotions/diary/' + dateStr)
      .then(function(response) {
        if (response.data && response.data.emotion) {
          setSelectedEmotion(response.data.emotion);
        } else {
          setSelectedEmotion(null);
        }
      })
      .catch(function(error) {
        console.error('Failed to fetch date emotion:', error);
        setSelectedEmotion(null);
      });
  }

  function fetchSuggestions(emotionName) {
    api.get('/tasks/suggestions', { params: { emotion: emotionName, limit: 5 } })
      .then(function(response) {
        setSuggestedTasks(response.data);
        setShowSuggestions(true);
      })
      .catch(function(error) {
        console.error('Failed to fetch suggestions:', error);
      });
  }

  function handleToggle(task) {
    api.put('/tasks/' + task.id, { is_completed: !task.is_completed })
      .then(function() {
        fetchTasks();
      })
      .catch(function(error) {
        console.error('Failed to toggle task:', error);
      });
  }

  function handleAddSuggestion(suggestion) {
    var emotionName = selectedEmotion ? selectedEmotion.name : null;
    
    api.post('/tasks', {
      title: suggestion.title,
      category: suggestion.category,
      priority: suggestion.priority,
      task_date: format(selectedDate, 'yyyy-MM-dd'),
      recommended_for_emotion: emotionName
    }).then(function() {
      fetchTasks();
    }).catch(function(error) {
      console.error('Failed to add suggestion:', error);
    });
  }

  function handleGenerateClick() {
    if (selectedEmotion) {
      fetchSuggestions(selectedEmotion.name);
    }
  }

  function handleCloseSuggestions() {
    setShowSuggestions(false);
  }

  // Filter tasks
  var incompleteTasks = [];
  var completedTasks = [];
  for (var i = 0; i < tasks.length; i++) {
    if (tasks[i].is_completed) {
      completedTasks.push(tasks[i]);
    } else {
      incompleteTasks.push(tasks[i]);
    }
  }

  if (loading) {
    return <div className="loading-screen">Loading tasks...</div>;
  }

  var dateDisplay = format(selectedDate, 'MMM d, yyyy');

  return (
    <div className="tasks-page">
      <header className="page-header">
        <div className="header-title-row">
          <h1>My Tasks</h1>
          <span className="date-display">{dateDisplay}</span>
        </div>
        <div className="header-actions">
          <button 
            className="btn-primary"
            onClick={handleGenerateClick}
            disabled={!selectedEmotion}
          >
            <Sparkles size={18} />
            Generate Emotion Tasks
          </button>
        </div>
      </header>

      {showSuggestions && suggestedTasks.length > 0 && (
        <div className="suggestions-panel card">
          <div className="panel-header">
            <h3>Suggested Tasks for {selectedEmotion ? selectedEmotion.name : ''} Mood</h3>
            <button className="close-btn" onClick={handleCloseSuggestions}>
              <X size={18} />
            </button>
          </div>
          <div className="suggestions-list">
            {suggestedTasks.map(function(suggestion, index) {
              return (
                <div key={index} className="suggestion-item">
                  <div className="suggestion-content">
                    <p>{suggestion.title}</p>
                    <span className="category-tag">{suggestion.category}</span>
                  </div>
                  <button 
                    className="btn-small"
                    onClick={function() { handleAddSuggestion(suggestion); }}
                  >
                    Add
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}

      <div className="tasks-content">
        <section className="tasks-section">
          <h2>To Do ({incompleteTasks.length})</h2>
          {incompleteTasks.length > 0 ? (
            <div className="task-list">
              {incompleteTasks.map(function(task) {
                return <TaskCard key={task.id} task={task} onToggle={handleToggle} mode="tasks" />;
              })}
            </div>
          ) : (
            <p className="empty-state">No pending tasks for this date.</p>
          )}
        </section>

        <section className="tasks-section completed">
          <h2>Completed ({completedTasks.length})</h2>
          {completedTasks.length > 0 ? (
            <div className="task-list">
              {completedTasks.map(function(task) {
                return <TaskCard key={task.id} task={task} onToggle={handleToggle} mode="tasks" />;
              })}
            </div>
          ) : (
            <p className="empty-state">No completed tasks for this date.</p>
          )}
        </section>
      </div>
    </div>
  );
}

export default Tasks;
