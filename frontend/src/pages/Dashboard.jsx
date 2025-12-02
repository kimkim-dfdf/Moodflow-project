import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useDate } from '../context/DateContext';
import EmotionSelector from '../components/EmotionSelector';
import TaskCard from '../components/TaskCard';
import api from '../api/axios';
import { format, isToday } from 'date-fns';
import { Music, CheckCircle2, Calendar, ExternalLink } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

function getEmotionColor(name) {
  if (name === 'Happy') return '#FFD93D';
  if (name === 'Sad') return '#6B7FD7';
  if (name === 'Tired') return '#A8A8A8';
  if (name === 'Angry') return '#FF6B6B';
  if (name === 'Stressed') return '#FF9F43';
  return '#95A5A6';
}

function MusicCard({ music }) {
  return (
    <div className="music-card">
      <div className="music-icon">
        <Music size={24} />
      </div>
      <div className="music-info">
        <h4 className="music-title">{music.title}</h4>
        <p className="music-artist">{music.artist}</p>
        <span className="music-genre">{music.genre}</span>
      </div>
      <div className="music-links">
        {music.youtube_url && (
          <a 
            href={music.youtube_url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="music-link youtube"
          >
            <ExternalLink size={16} />
            YouTube
          </a>
        )}
      </div>
    </div>
  );
}

function MoodStats({ stats }) {
  if (!stats || !stats.counts) {
    return (
      <div className="mood-stats empty">
        <p>No mood data yet. Start tracking your emotions!</p>
      </div>
    );
  }

  var countKeys = Object.keys(stats.counts);
  if (countKeys.length === 0) {
    return (
      <div className="mood-stats empty">
        <p>No mood data yet. Start tracking your emotions!</p>
      </div>
    );
  }

  var data = [];
  for (var i = 0; i < countKeys.length; i++) {
    var name = countKeys[i];
    var value = stats.counts[name];
    data.push({
      name: name,
      value: value,
      color: getEmotionColor(name)
    });
  }

  return (
    <div className="mood-stats">
      <h3>Your Mood This Week</h3>
      <div className="stats-chart">
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={50}
              outerRadius={70}
              paddingAngle={2}
              dataKey="value"
            >
              {data.map(function(entry, index) {
                return <Cell key={'cell-' + index} fill={entry.color} />;
              })}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <div className="dominant-mood">
        <span>Most common mood:</span>
        <strong>{stats.dominant_emotion}</strong>
      </div>
    </div>
  );
}

function Dashboard() {
  const { user } = useAuth();
  const { selectedDate, setSelectedDate } = useDate();
  const [selectedEmotion, setSelectedEmotion] = useState(null);
  const [recommendedTasks, setRecommendedTasks] = useState([]);
  const [suggestedTasks, setSuggestedTasks] = useState([]);
  const [musicRecommendations, setMusicRecommendations] = useState([]);
  const [taskSummary, setTaskSummary] = useState({ total: 0, completed: 0, pending: 0 });
  const [moodStats, setMoodStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [addedTasks, setAddedTasks] = useState(new Set());
  const [allTasks, setAllTasks] = useState([]);

  useEffect(function() {
    fetchDashboardData();
  }, [selectedDate]);

  useEffect(function() {
    if (selectedEmotion) {
      fetchRecommendations(selectedEmotion.name);
    }
  }, [selectedEmotion]);

  function fetchDashboardData() {
    var dateStr = format(selectedDate, 'yyyy-MM-dd');
    
    Promise.all([
      api.get('/dashboard/summary', { params: { date: dateStr } }),
      api.get('/emotions/diary/' + dateStr),
      api.get('/tasks', { params: { date: dateStr } })
    ]).then(function(results) {
      var summaryRes = results[0];
      var dateEmotionRes = results[1];
      var tasksRes = results[2];

      var summary = summaryRes.data;
      setTaskSummary(summary.task_summary);
      setMoodStats(summary.weekly_mood_stats);
      setAllTasks(tasksRes.data);
      
      var existingTitles = new Set();
      for (var i = 0; i < tasksRes.data.length; i++) {
        existingTitles.add(tasksRes.data[i].title);
      }
      setAddedTasks(existingTitles);

      if (dateEmotionRes.data && dateEmotionRes.data.emotion) {
        setSelectedEmotion(dateEmotionRes.data.emotion);
      } else {
        setSelectedEmotion(null);
        setRecommendedTasks([]);
        setSuggestedTasks([]);
        setMusicRecommendations([]);
      }
      setLoading(false);
    }).catch(function(error) {
      console.error('Failed to fetch dashboard data:', error);
      setSelectedEmotion(null);
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
      setMusicRecommendations(results[2].data);
    }).catch(function(error) {
      console.error('Failed to fetch recommendations:', error);
    });
  }

  function handleTaskToggle(task) {
    api.put('/tasks/' + task.id, { is_completed: !task.is_completed })
      .then(function() {
        fetchDashboardData();
        if (selectedEmotion) {
          fetchRecommendations(selectedEmotion.name);
        }
      })
      .catch(function(error) {
        console.error('Failed to toggle task:', error);
      });
  }

  function handleAddSuggestedTask(suggestion) {
    if (addedTasks.has(suggestion.title)) {
      return;
    }
    
    var dateStr = format(selectedDate, 'yyyy-MM-dd');
    var emotionName = selectedEmotion ? selectedEmotion.name : null;
    
    api.post('/tasks', {
      title: suggestion.title,
      category: suggestion.category,
      priority: suggestion.priority,
      task_date: dateStr,
      recommended_for_emotion: emotionName
    }).then(function() {
      var newSet = new Set(addedTasks);
      newSet.add(suggestion.title);
      setAddedTasks(newSet);
      fetchDashboardData();
      if (selectedEmotion) {
        fetchRecommendations(selectedEmotion.name);
      }
    }).catch(function(error) {
      if (error.response && error.response.status === 409) {
        var newSet = new Set(addedTasks);
        newSet.add(suggestion.title);
        setAddedTasks(newSet);
      }
      console.error('Failed to add task:', error);
    });
  }

  function handleEmotionSelect(emotion) {
    setSelectedEmotion(emotion);
    
    api.post('/emotions/record', {
      emotion_id: emotion.id,
      date: format(selectedDate, 'yyyy-MM-dd')
    }).catch(function(error) {
      console.error('Failed to record emotion:', error);
    });
  }

  function getGreeting() {
    var hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 18) return 'Good Afternoon';
    return 'Good Evening';
  }

  function getDateDisplay() {
    var dateText = format(selectedDate, 'EEEE, MMMM d, yyyy');
    if (isToday(selectedDate)) {
      return dateText + ' (Today)';
    }
    return dateText;
  }

  if (loading) {
    return <div className="loading-screen">Loading your dashboard...</div>;
  }

  var username = user ? user.username : 'User';

  return (
    <div className="dashboard-page">
      <header className="dashboard-header">
        <div className="greeting">
          <h1>{getGreeting()}, {username}!</h1>
          <p className="date-display">
            <Calendar size={16} />
            {getDateDisplay()}
          </p>
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
              <h3>How are you feeling today?</h3>
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
                  <h3>Recommended Tasks for You</h3>
                </div>
                {recommendedTasks.length > 0 ? (
                  <div className="task-list">
                    {recommendedTasks.map(function(item) {
                      var taskWithScore = Object.assign({}, item.task, { score: item.score });
                      return (
                        <TaskCard 
                          key={item.task.id} 
                          task={taskWithScore} 
                          onToggle={handleTaskToggle}
                          showScore={true}
                          selectedDate={selectedDate}
                        />
                      );
                    })}
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
                  {suggestedTasks.map(function(suggestion, index) {
                    var isAdded = addedTasks.has(suggestion.title);
                    var btnClass = 'add-btn';
                    if (isAdded) {
                      btnClass = 'add-btn added';
                    }
                    return (
                      <div key={index} className="suggestion-card">
                        <p>{suggestion.title}</p>
                        <div className="suggestion-meta">
                          <span className="category">{suggestion.category}</span>
                          <button 
                            className={btnClass}
                            onClick={function() { handleAddSuggestedTask(suggestion); }}
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
                  {musicRecommendations.map(function(music) {
                    return <MusicCard key={music.id} music={music} />;
                  })}
                </div>
              </section>
            </>
          )}
        </div>

        <aside className="dashboard-sidebar">
          <section className="card stats-section">
            <MoodStats stats={moodStats} />
          </section>
        </aside>
      </div>
    </div>
  );
}

export default Dashboard;
