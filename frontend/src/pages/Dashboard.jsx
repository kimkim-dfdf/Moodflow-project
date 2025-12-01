import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import EmotionSelector from '../components/EmotionSelector';
import TaskCard from '../components/TaskCard';
import MusicCard from '../components/MusicCard';
import MiniCalendar from '../components/MiniCalendar';
import MoodStats from '../components/MoodStats';
import api from '../api/axios';
import { format, isToday } from 'date-fns';
import { Sparkles, Music, CheckCircle2, Calendar } from 'lucide-react';

const Dashboard = () => {
  const { user } = useAuth();
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [selectedEmotion, setSelectedEmotion] = useState(null);
  const [recommendedTasks, setRecommendedTasks] = useState([]);
  const [suggestedTasks, setSuggestedTasks] = useState([]);
  const [musicRecommendations, setMusicRecommendations] = useState([]);
  const [taskSummary, setTaskSummary] = useState({ total: 0, completed: 0, pending: 0 });
  const [moodStats, setMoodStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [addedTasks, setAddedTasks] = useState(new Set());
  const [allTasks, setAllTasks] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, [selectedDate]);

  useEffect(() => {
    if (selectedEmotion) {
      fetchRecommendations(selectedEmotion.name);
    }
  }, [selectedEmotion]);

  const fetchDashboardData = async () => {
    try {
      const dateStr = format(selectedDate, 'yyyy-MM-dd');
      const [summaryRes, dateEmotionRes, tasksRes] = await Promise.all([
        api.get('/dashboard/summary', { params: { date: dateStr } }),
        api.get(`/emotions/diary/${dateStr}`),
        api.get('/tasks', { params: { date: dateStr } })
      ]);

      const summary = summaryRes.data;
      setTaskSummary(summary.task_summary);
      setMoodStats(summary.weekly_mood_stats);
      setAllTasks(tasksRes.data);
      
      const existingTitles = new Set(tasksRes.data.map(t => t.title));
      setAddedTasks(existingTitles);

      if (dateEmotionRes.data && dateEmotionRes.data.emotion) {
        setSelectedEmotion(dateEmotionRes.data.emotion);
      } else {
        setSelectedEmotion(null);
        setRecommendedTasks([]);
        setSuggestedTasks([]);
        setMusicRecommendations([]);
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      setSelectedEmotion(null);
    } finally {
      setLoading(false);
    }
  };

  const fetchRecommendations = async (emotionName) => {
    try {
      const dateStr = format(selectedDate, 'yyyy-MM-dd');
      const [tasksRes, suggestionsRes, musicRes] = await Promise.all([
        api.get('/tasks/recommended', { params: { emotion: emotionName, limit: 3, date: dateStr } }),
        api.get('/tasks/suggestions', { params: { emotion: emotionName, limit: 3 } }),
        api.get('/music/recommendations', { params: { emotion: emotionName, limit: 4 } })
      ]);

      setRecommendedTasks(tasksRes.data);
      setSuggestedTasks(suggestionsRes.data);
      setMusicRecommendations(musicRes.data);
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
    }
  };

  const handleTaskToggle = async (task) => {
    try {
      await api.put(`/tasks/${task.id}`, { is_completed: !task.is_completed });
      fetchDashboardData();
      if (selectedEmotion) {
        fetchRecommendations(selectedEmotion.name);
      }
    } catch (error) {
      console.error('Failed to toggle task:', error);
    }
  };

  const handleAddSuggestedTask = async (suggestion) => {
    if (addedTasks.has(suggestion.title)) {
      return;
    }
    
    try {
      const dateStr = format(selectedDate, 'yyyy-MM-dd');
      await api.post('/tasks', {
        title: suggestion.title,
        category: suggestion.category,
        priority: suggestion.priority,
        task_date: dateStr,
        recommended_for_emotion: selectedEmotion?.name
      });
      setAddedTasks(prev => new Set([...prev, suggestion.title]));
      fetchDashboardData();
      if (selectedEmotion) {
        fetchRecommendations(selectedEmotion.name);
      }
    } catch (error) {
      if (error.response?.status === 409) {
        setAddedTasks(prev => new Set([...prev, suggestion.title]));
      }
      console.error('Failed to add task:', error);
    }
  };

  const handleDateSelect = (date) => {
    setSelectedDate(date);
    setLoading(true);
  };

  const handleEmotionSelect = async (emotion) => {
    setSelectedEmotion(emotion);
    
    try {
      await api.post('/emotions/record', {
        emotion_id: emotion.id,
        date: format(selectedDate, 'yyyy-MM-dd')
      });
    } catch (error) {
      console.error('Failed to record emotion:', error);
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 18) return 'Good Afternoon';
    return 'Good Evening';
  };

  const getDateDisplay = () => {
    if (isToday(selectedDate)) {
      return format(selectedDate, 'EEEE, MMMM d, yyyy') + ' (Today)';
    }
    return format(selectedDate, 'EEEE, MMMM d, yyyy');
  };

  if (loading) {
    return <div className="loading-screen">Loading your dashboard...</div>;
  }

  return (
    <div className="dashboard-page">
      <header className="dashboard-header">
        <div className="greeting">
          <h1>{getGreeting()}, {user?.username}!</h1>
          <p className="date-display">
            <Calendar size={16} />
            {getDateDisplay()}
          </p>
          {!isToday(selectedDate) && (
            <button 
              className="today-btn"
              onClick={() => handleDateSelect(new Date())}
            >
              Back to Today
            </button>
          )}
        </div>
        <div className="task-summary-badges">
          <div className="badge total">
            <span className="badge-value">{taskSummary.total}</span>
            <span className="badge-label">Total Tasks</span>
          </div>
          <div className="badge completed">
            <CheckCircle2 size={16} />
            <span className="badge-value">{taskSummary.completed}</span>
            <span className="badge-label">Completed</span>
          </div>
          <div className="badge pending">
            <span className="badge-value">{taskSummary.pending}</span>
            <span className="badge-label">Pending</span>
          </div>
        </div>
      </header>

      <div className="dashboard-grid">
        <div className="dashboard-main">
          <section className="card emotion-section">
            <div className="emotion-header">
              <h3>How are you feeling {isToday(selectedDate) ? 'today' : 'on this day'}?</h3>
              {!selectedEmotion && (
                <p className="emotion-hint">Select your mood to get personalized recommendations</p>
              )}
            </div>
            <EmotionSelector 
              selectedEmotion={selectedEmotion} 
              onSelect={handleEmotionSelect}
              selectedDate={selectedDate}
            />
          </section>

          {selectedEmotion && (
            <>
              <section className="card recommendations-section">
                <div className="section-header">
                  <h3><Sparkles size={20} /> Recommended Tasks for You</h3>
                </div>
                {recommendedTasks.length > 0 ? (
                  <div className="task-list">
                    {recommendedTasks.map((item) => (
                      <TaskCard 
                        key={item.task.id} 
                        task={{ ...item.task, score: item.score }} 
                        onToggle={handleTaskToggle}
                        showScore={true}
                      />
                    ))}
                  </div>
                ) : (
                  <p className="empty-state">No tasks yet. Add some tasks to get personalized recommendations!</p>
                )}
              </section>

              <section className="card suggestions-section">
                <div className="section-header">
                  <h3>Suggested Activities for {selectedEmotion.name} Mood</h3>
                </div>
                <div className="suggestions-grid">
                  {suggestedTasks.map((suggestion, index) => {
                    const isAdded = addedTasks.has(suggestion.title);
                    return (
                      <div key={index} className="suggestion-card">
                        <p>{suggestion.title}</p>
                        <div className="suggestion-meta">
                          <span className="category">{suggestion.category}</span>
                          <button 
                            className={`add-btn ${isAdded ? 'added' : ''}`}
                            onClick={() => handleAddSuggestedTask(suggestion)}
                            disabled={isAdded}
                          >
                            {isAdded ? 'Added' : 'Add to Tasks'}
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </section>

              <section className="card music-section">
                <div className="section-header">
                  <h3><Music size={20} /> Music for Your Mood</h3>
                </div>
                <div className="music-grid">
                  {musicRecommendations.map((music) => (
                    <MusicCard key={music.id} music={music} />
                  ))}
                </div>
              </section>
            </>
          )}
        </div>

        <aside className="dashboard-sidebar">
          <section className="card calendar-section">
            <h3 className="calendar-title">Select a Date</h3>
            <MiniCalendar 
              onDateSelect={handleDateSelect}
              selectedDate={selectedDate}
            />
          </section>

          <section className="card stats-section">
            <MoodStats stats={moodStats} />
          </section>
        </aside>
      </div>
    </div>
  );
};

export default Dashboard;
