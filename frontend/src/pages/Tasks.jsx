import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import api from '../api/axios';
import TaskCard from '../components/TaskCard';
import MiniCalendar from '../components/MiniCalendar';
import { Plus, Filter, Sparkles, X, Calendar, RotateCcw } from 'lucide-react';
import { format, isToday } from 'date-fns';

const CATEGORIES = ['Work', 'Study', 'Health', 'Personal'];
const PRIORITIES = ['Low', 'Medium', 'High'];

const Tasks = () => {
  const location = useLocation();
  const initialDate = location.state?.selectedDate 
    ? new Date(location.state.selectedDate) 
    : new Date();

  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [filter, setFilter] = useState({ status: 'all', category: 'all' });
  const [emotions, setEmotions] = useState([]);
  const [selectedEmotion, setSelectedEmotion] = useState(null);
  const [suggestedTasks, setSuggestedTasks] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedDate, setSelectedDate] = useState(initialDate);
  const [showCalendar, setShowCalendar] = useState(false);

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: 'Personal',
    priority: 'Medium',
    due_date: ''
  });

  useEffect(() => {
    if (location.state?.selectedDate) {
      const newDate = new Date(location.state.selectedDate);
      setSelectedDate(newDate);
    }
  }, [location.state]);

  useEffect(() => {
    fetchTasks();
    fetchEmotions();
    fetchDateEmotion();
  }, [filter, selectedDate]);

  const fetchTasks = async () => {
    try {
      const params = { date: format(selectedDate, 'yyyy-MM-dd') };
      if (filter.status !== 'all') params.status = filter.status;
      if (filter.category !== 'all') params.category = filter.category;

      const response = await api.get('/tasks', { params });
      setTasks(response.data);
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
    } finally {
      setLoading(false);
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const taskData = {
        ...formData,
        task_date: format(selectedDate, 'yyyy-MM-dd')
      };
      
      if (editingTask) {
        await api.put(`/tasks/${editingTask.id}`, taskData);
      } else {
        await api.post('/tasks', taskData);
      }
      setShowModal(false);
      resetForm();
      fetchTasks();
    } catch (error) {
      console.error('Failed to save task:', error);
    }
  };

  const handleEdit = (task) => {
    setEditingTask(task);
    setFormData({
      title: task.title,
      description: task.description || '',
      category: task.category,
      priority: task.priority,
      due_date: task.due_date || ''
    });
    setShowModal(true);
  };

  const handleDelete = async (taskId) => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      try {
        await api.delete(`/tasks/${taskId}`);
        fetchTasks();
      } catch (error) {
        console.error('Failed to delete task:', error);
      }
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

  const resetForm = () => {
    setEditingTask(null);
    setFormData({
      title: '',
      description: '',
      category: 'Personal',
      priority: 'Medium',
      due_date: ''
    });
  };

  const openNewTaskModal = () => {
    resetForm();
    setShowModal(true);
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
            className="btn-secondary"
            onClick={() => selectedEmotion && fetchSuggestions(selectedEmotion.name)}
            disabled={!selectedEmotion}
          >
            <Sparkles size={18} />
            Generate Emotion Tasks
          </button>
          <button className="btn-primary" onClick={openNewTaskModal}>
            <Plus size={18} />
            Add Task
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

      <div className="filters-bar">
        <div className="filter-group">
          <Filter size={16} />
          <select 
            value={filter.status} 
            onChange={(e) => setFilter({ ...filter, status: e.target.value })}
          >
            <option value="all">All Status</option>
            <option value="incomplete">Incomplete</option>
            <option value="completed">Completed</option>
          </select>
          <select 
            value={filter.category} 
            onChange={(e) => setFilter({ ...filter, category: e.target.value })}
          >
            <option value="all">All Categories</option>
            {CATEGORIES.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>
      </div>

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

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingTask ? 'Edit Task' : 'New Task'}</h2>
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
                  placeholder="Task title"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="description">Description</label>
                <textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Task description (optional)"
                  rows={3}
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="category">Category</label>
                  <select
                    id="category"
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  >
                    {CATEGORIES.map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="priority">Priority</label>
                  <select
                    id="priority"
                    value={formData.priority}
                    onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                  >
                    {PRIORITIES.map(pri => (
                      <option key={pri} value={pri}>{pri}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="due_date">Due Date</label>
                <input
                  type="date"
                  id="due_date"
                  value={formData.due_date}
                  onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                />
              </div>

              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  {editingTask ? 'Update Task' : 'Create Task'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Tasks;
