/**
 * Tasks 페이지 컴포넌트
 * - 할일 목록 조회, 추가, 수정, 삭제
 * - 날짜별 할일 관리
 * - 감정 기반 할일 제안
 */

import { useState, useEffect } from 'react';
import { useDate } from '../context/DateContext';
import api from '../api/axios';
import TaskCard from '../components/TaskCard';
import MiniCalendar from '../components/MiniCalendar';
import { Plus, Filter, Sparkles, X, Calendar, RotateCcw } from 'lucide-react';
import { format, isToday } from 'date-fns';


// 카테고리와 우선순위 옵션
const CATEGORIES = ['Work', 'Study', 'Health', 'Personal'];
const PRIORITIES = ['Low', 'Medium', 'High'];


const Tasks = () => {
  // 공유 날짜 컨텍스트 사용
  const { selectedDate, setSelectedDate } = useDate();

  // 상태 관리
  const [tasks, setTasks] = useState([]);                              // 할일 목록
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);                   // 할일 추가/수정 모달
  const [editingTask, setEditingTask] = useState(null);                // 수정 중인 할일
  const [filter, setFilter] = useState({ status: 'all', category: 'all' });
  const [emotions, setEmotions] = useState([]);                        // 감정 목록
  const [selectedEmotion, setSelectedEmotion] = useState(null);        // 선택된 날짜의 감정
  const [suggestedTasks, setSuggestedTasks] = useState([]);            // 제안 할일
  const [showSuggestions, setShowSuggestions] = useState(false);       // 제안 패널 표시
  const [showCalendar, setShowCalendar] = useState(false);             // 캘린더 드롭다운

  // 새 할일 폼 데이터
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: 'Personal',
    priority: 'Medium',
    due_date: ''
  });


  // 날짜나 필터가 바뀔 때마다 데이터 새로고침
  useEffect(() => {
    fetchTasks();
    fetchEmotions();
    fetchDateEmotion();
  }, [filter, selectedDate]);


  /**
   * 할일 목록 가져오기
   */
  const fetchTasks = async () => {
    try {
      const params = { date: format(selectedDate, 'yyyy-MM-dd') };
      
      // 필터 적용
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


  /**
   * 감정 목록 가져오기 (제안 기능용)
   */
  const fetchEmotions = async () => {
    try {
      const response = await api.get('/emotions');
      setEmotions(response.data);
    } catch (error) {
      console.error('Failed to fetch emotions:', error);
    }
  };


  /**
   * 선택된 날짜의 감정 기록 가져오기
   */
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


  /**
   * 감정 기반 할일 제안 가져오기
   */
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


  /**
   * 할일 생성/수정 폼 제출
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const taskData = {
        ...formData,
        task_date: format(selectedDate, 'yyyy-MM-dd')
      };
      
      if (editingTask) {
        // 수정 모드
        await api.put(`/tasks/${editingTask.id}`, taskData);
      } else {
        // 새로 생성
        await api.post('/tasks', taskData);
      }
      
      setShowModal(false);
      resetForm();
      fetchTasks();
    } catch (error) {
      console.error('Failed to save task:', error);
    }
  };


  /**
   * 할일 수정 모드 진입
   */
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


  /**
   * 할일 삭제
   */
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


  /**
   * 할일 완료 상태 토글
   */
  const handleToggle = async (task) => {
    try {
      await api.put(`/tasks/${task.id}`, { 
        is_completed: !task.is_completed 
      });
      fetchTasks();
    } catch (error) {
      console.error('Failed to toggle task:', error);
    }
  };


  /**
   * 제안된 할일 추가
   */
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


  /**
   * 폼 초기화
   */
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


  /**
   * 새 할일 모달 열기
   */
  const openNewTaskModal = () => {
    resetForm();
    setShowModal(true);
  };


  /**
   * 날짜 선택 처리
   */
  const handleDateSelect = (date) => {
    setSelectedDate(date);
    setShowCalendar(false);
    setLoading(true);
  };


  /**
   * 오늘 날짜로 돌아가기
   */
  const handleBackToToday = () => {
    setSelectedDate(new Date());
    setLoading(true);
  };


  // 완료/미완료 할일 분리
  const incompleteTasks = tasks.filter(t => !t.is_completed);
  const completedTasks = tasks.filter(t => t.is_completed);


  if (loading) {
    return <div className="loading-screen">Loading tasks...</div>;
  }


  return (
    <div className="tasks-page">
      {/* 페이지 헤더 */}
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
        
        {/* 액션 버튼들 */}
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

      {/* 캘린더 드롭다운 */}
      {showCalendar && (
        <div className="calendar-dropdown card">
          <MiniCalendar 
            onDateSelect={handleDateSelect}
            selectedDate={selectedDate}
          />
        </div>
      )}

      {/* 필터 바 */}
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

      {/* 할일 제안 패널 */}
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

      {/* 할일 목록 */}
      <div className="tasks-content">
        {/* 미완료 할일 */}
        <section className="tasks-section">
          <h2>To Do ({incompleteTasks.length})</h2>
          {incompleteTasks.length > 0 ? (
            <div className="task-list">
              {incompleteTasks.map((task) => (
                <TaskCard 
                  key={task.id} 
                  task={task} 
                  onToggle={handleToggle} 
                  mode="tasks" 
                />
              ))}
            </div>
          ) : (
            <p className="empty-state">No pending tasks for this date.</p>
          )}
        </section>

        {/* 완료된 할일 */}
        <section className="tasks-section completed">
          <h2>Completed ({completedTasks.length})</h2>
          {completedTasks.length > 0 ? (
            <div className="task-list">
              {completedTasks.map((task) => (
                <TaskCard 
                  key={task.id} 
                  task={task} 
                  onToggle={handleToggle} 
                  mode="tasks" 
                />
              ))}
            </div>
          ) : (
            <p className="empty-state">No completed tasks for this date.</p>
          )}
        </section>
      </div>

      {/* 할일 추가/수정 모달 */}
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
              {/* 제목 */}
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

              {/* 설명 */}
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

              {/* 카테고리와 우선순위 */}
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

              {/* 마감일 */}
              <div className="form-group">
                <label htmlFor="due_date">Due Date</label>
                <input
                  type="date"
                  id="due_date"
                  value={formData.due_date}
                  onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                />
              </div>

              {/* 버튼들 */}
              <div className="modal-actions">
                <button 
                  type="button" 
                  className="btn-secondary" 
                  onClick={() => setShowModal(false)}
                >
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
