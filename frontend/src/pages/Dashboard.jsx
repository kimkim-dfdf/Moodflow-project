import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useDate } from '../context/DateContext';
import EmotionSelector from '../components/EmotionSelector';
import TaskCard from '../components/TaskCard';
import MiniCalendar from '../components/MiniCalendar';
import api from '../api/axios';
import { format, isToday } from 'date-fns';
import { Music, CheckCircle2, Calendar, ExternalLink } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

function Dashboard() {
  const { user } = useAuth();
  const { selectedDate, setSelectedDate } = useDate();
  const [selectedEmotion, setSelectedEmotion] = useState(null);
  const [recommendedTasks, setRecommendedTasks] = useState([]);
  const [suggestedTasks, setSuggestedTasks] = useState([]);
  const [musicList, setMusicList] = useState([]);
  const [taskSummary, setTaskSummary] = useState({ total: 0, completed: 0, pending: 0 });
  const [moodStats, setMoodStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [addedTasks, setAddedTasks] = useState(new Set());
  const [calendarKey, setCalendarKey] = useState(0);

  useEffect(function() {
    fetchData();
  }, [selectedDate]);

  useEffect(function() {
    if (selectedEmotion) {
      fetchRecommendations(selectedEmotion.name);
    }
  }, [selectedEmotion]);

  function fetchData() {
    var dateStr = format(selectedDate, 'yyyy-MM-dd');
    
    Promise.all([
      api.get('/dashboard/summary', { params: { date: dateStr } }),
      api.get('/emotions/diary/' + dateStr),
      api.get('/tasks', { params: { date: dateStr } })
    ]).then(function(results) {
      var summary = results[0].data;
      var emotionRes = results[1].data;
      var tasksRes = results[2].data;
      
      setTaskSummary(summary.task_summary);
      setMoodStats(summary.weekly_mood_stats);
      
      var titles = new Set();
      for (var i = 0; i < tasksRes.length; i++) {
        titles.add(tasksRes[i].title);
      }
      setAddedTasks(titles);

      if (emotionRes && emotionRes.emotion) {
        setSelectedEmotion(emotionRes.emotion);
      } else {
        setSelectedEmotion(null);
        setRecommendedTasks([]);
        setSuggestedTasks([]);
        setMusicList([]);
      }
      setLoading(false);
    }).catch(function(error) {
      console.error('Error:', error);
      setLoading(false);
    });
  }

  function fetchRecommendations(emotionName) {
    var dateStr = format(selectedDate, 'yyyy-MM-dd');
    
    Promise.all([
      api.get('/tasks/recommended', { params: { emotion: emotionName, limit: 3, date: dateStr } }),
      api.get('/tasks/suggestions', { params: { emotion: emotionName, limit: 3 } }),
      api.get('/music/recommendations', { params: { emotion: emotionName, limit: 4 } })
    ]).then(function(results) {
      setRecommendedTasks(results[0].data);
      setSuggestedTasks(results[1].data);
      setMusicList(results[2].data);
    }).catch(function(error) {
      console.error('Error:', error);
    });
  }

  function handleTaskToggle(task) {
    api.put('/tasks/' + task.id, { is_completed: !task.is_completed })
      .then(function() {
        fetchData();
        if (selectedEmotion) {
          fetchRecommendations(selectedEmotion.name);
        }
      });
  }

  function handleAddTask(suggestion) {
    if (addedTasks.has(suggestion.title)) return;
    
    var dateStr = format(selectedDate, 'yyyy-MM-dd');
    api.post('/tasks', {
      title: suggestion.title,
      category: suggestion.category,
      priority: suggestion.priority,
      task_date: dateStr,
      recommended_for_emotion: selectedEmotion ? selectedEmotion.name : null
    }).then(function() {
      var newSet = new Set(addedTasks);
      newSet.add(suggestion.title);
      setAddedTasks(newSet);
      fetchData();
      if (selectedEmotion) {
        fetchRecommendations(selectedEmotion.name);
      }
    }).catch(function(error) {
      if (error.response && error.response.status === 409) {
        var newSet = new Set(addedTasks);
        newSet.add(suggestion.title);
        setAddedTasks(newSet);
      }
    });
  }

  function handleEmotionSelect(emotion) {
    setSelectedEmotion(emotion);
    api.post('/emotions/record', {
      emotion_id: emotion.id,
      date: format(selectedDate, 'yyyy-MM-dd')
    }).then(function() {
      setCalendarKey(calendarKey + 1);
    });
  }

  function getGreeting() {
    var hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 18) return 'Good Afternoon';
    return 'Good Evening';
  }

  if (loading) {
    return <div className="loading-screen">Loading...</div>;
  }

  return (
    <div className="dashboard-page">
      <header className="dashboard-header">
        <div className="greeting">
          <h1>{getGreeting()}, {user ? user.username : ''}!</h1>
          <p className="date-display">
            <Calendar size={16} />
            {format(selectedDate, 'EEEE, MMMM d, yyyy')}
            {isToday(selectedDate) ? ' (Today)' : ''}
          </p>
          {!isToday(selectedDate) && (
            <button className="today-btn" onClick={function() { setSelectedDate(new Date()); }}>
              Back to Today
            </button>
          )}
        </div>
        <div className="task-summary-badges">
          <div className="badge"><span className="badge-value">{taskSummary.total}</span><span className="badge-label">Total</span></div>
          <div className="badge completed"><CheckCircle2 size={16} /><span className="badge-value">{taskSummary.completed}</span><span className="badge-label">Done</span></div>
          <div className="badge"><span className="badge-value">{taskSummary.pending}</span><span className="badge-label">Pending</span></div>
        </div>
      </header>

      <div className="dashboard-grid">
        <div className="dashboard-main">
          <section className="card">
            <div className="emotion-header">
              <h3>How are you feeling?</h3>
              {!selectedEmotion && <p className="emotion-hint">Select your mood</p>}
            </div>
            <EmotionSelector selectedEmotion={selectedEmotion} onSelect={handleEmotionSelect} selectedDate={selectedDate} />
          </section>

          {selectedEmotion && (
            <>
              <section className="card">
                <div className="section-header"><h3>Recommended Tasks</h3></div>
                {recommendedTasks.length > 0 ? (
                  <div className="task-list">
                    {recommendedTasks.map(function(item) {
                      return <TaskCard key={item.task.id} task={{ ...item.task, score: item.score }} onToggle={handleTaskToggle} showScore={true} selectedDate={selectedDate} />;
                    })}
                  </div>
                ) : (
                  <p className="empty-state">No tasks yet</p>
                )}
              </section>

              <section className="card">
                <div className="section-header"><h3>Suggested for {selectedEmotion.name}</h3></div>
                <div className="suggestions-grid">
                  {suggestedTasks.map(function(s, i) {
                    var isAdded = addedTasks.has(s.title);
                    return (
                      <div key={i} className="suggestion-card">
                        <p>{s.title}</p>
                        <div className="suggestion-meta">
                          <span className="category">{s.category}</span>
                          <button className={'add-btn ' + (isAdded ? 'added' : '')} onClick={function() { handleAddTask(s); }} disabled={isAdded}>
                            {isAdded ? 'Added' : 'Add'}
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </section>

              <section className="card">
                <div className="section-header"><h3><Music size={20} /> Music</h3></div>
                <div className="music-grid">
                  {musicList.map(function(m) {
                    return (
                      <div key={m.id} className="music-card">
                        <div className="music-icon"><Music size={24} /></div>
                        <div className="music-info">
                          <h4 className="music-title">{m.title}</h4>
                          <p className="music-artist">{m.artist}</p>
                          <span className="music-genre">{m.genre}</span>
                        </div>
                        {m.youtube_url && (
                          <div className="music-links">
                            <a href={m.youtube_url} target="_blank" rel="noopener noreferrer" className="music-link">
                              <ExternalLink size={16} /> YouTube
                            </a>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </section>
            </>
          )}
        </div>

        <aside className="dashboard-sidebar">
          <section className="card">
            <h3 className="calendar-title">Select Date</h3>
            <MiniCalendar key={calendarKey} onDateSelect={setSelectedDate} selectedDate={selectedDate} />
          </section>

          <section className="card mood-stats">
            <h3>Weekly Mood</h3>
            {moodStats && moodStats.counts && Object.keys(moodStats.counts).length > 0 ? (
              <>
                <ResponsiveContainer width="100%" height={180}>
                  <PieChart>
                    <Pie data={Object.entries(moodStats.counts).map(function(e) { return { name: e[0], value: e[1] }; })} cx="50%" cy="50%" innerRadius={40} outerRadius={60} dataKey="value">
                      {Object.keys(moodStats.counts).map(function(name, i) {
                        var colors = { Happy: '#FFD93D', Sad: '#6B7FD7', Tired: '#A8A8A8', Angry: '#FF6B6B', Stressed: '#FF9F43', Neutral: '#95A5A6' };
                        return <Cell key={i} fill={colors[name] || '#95A5A6'} />;
                      })}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
                <div className="dominant-mood"><span>Most common: </span><strong>{moodStats.dominant_emotion}</strong></div>
              </>
            ) : (
              <p>No mood data yet</p>
            )}
          </section>
        </aside>
      </div>
    </div>
  );
}

export default Dashboard;
