import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Navigate } from 'react-router-dom';
import api from '../api/axios';
import { 
  BarChart3, Users, CheckCircle2, Clock
} from 'lucide-react';

function Admin() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(function() {
    if (user && user.is_admin) {
      fetchData();
    }
  }, [user]);

  function fetchData() {
    setLoading(true);
    api.get('/admin/stats').then(function(response) {
      setStats(response.data);
      setLoading(false);
    }).catch(function() {
      setLoading(false);
    });
  }

  if (!user || !user.is_admin) {
    return <Navigate to="/dashboard" />;
  }

  if (loading) {
    return <div className="loading-screen">Loading...</div>;
  }

  return (
    <div className="admin-page">
      <header className="page-header">
        <h1><BarChart3 size={28} /> Admin Dashboard</h1>
        <p>View statistics and user activity</p>
      </header>

      {stats && (
        <div className="stats-section">
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon users"><Users size={24} /></div>
              <div className="stat-info">
                <span className="stat-value">{stats.total_users}</span>
                <span className="stat-label">Total Users</span>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon tasks"><CheckCircle2 size={24} /></div>
              <div className="stat-info">
                <span className="stat-value">{stats.tasks.total}</span>
                <span className="stat-label">Total Tasks</span>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon completed"><CheckCircle2 size={24} /></div>
              <div className="stat-info">
                <span className="stat-value">{stats.tasks.completed}</span>
                <span className="stat-label">Completed Tasks</span>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon pending"><Clock size={24} /></div>
              <div className="stat-info">
                <span className="stat-value">{stats.tasks.pending}</span>
                <span className="stat-label">Pending Tasks</span>
              </div>
            </div>
          </div>

          <div className="stats-details">
            <div className="detail-card">
              <h3><Users size={20} /> User Activity</h3>
              <div className="user-stats-list">
                {stats.users.map(function(u) {
                  return (
                    <div key={u.user_id} className="user-stat-row">
                      <div className="user-info">
                        <span className="user-name">{u.username}</span>
                        <span className="user-email">{u.email}</span>
                      </div>
                      <div className="user-metrics">
                        <span className="metric">
                          <CheckCircle2 size={14} /> {u.completed_tasks}/{u.total_tasks} tasks
                        </span>
                        <span className="metric">
                          {u.emotion_entries} mood entries
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="detail-card">
              <h3>Emotion Distribution</h3>
              <div className="emotion-stats-list">
                {stats.emotions.map(function(e) {
                  return (
                    <div key={e.emotion.id} className="emotion-stat-row">
                      <span className="emotion-emoji">{e.emotion.emoji}</span>
                      <span className="emotion-name">{e.emotion.name}</span>
                      <div className="emotion-bar-container">
                        <div 
                          className="emotion-bar" 
                          style={{ 
                            width: Math.min(e.count * 20, 100) + '%',
                            backgroundColor: e.emotion.color 
                          }}
                        ></div>
                      </div>
                      <span className="emotion-count">{e.count}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="detail-card">
              <h3>Tasks by Category</h3>
              <div className="category-stats-list">
                {Object.entries(stats.tasks.by_category || {}).map(function(entry) {
                  var category = entry[0];
                  var count = entry[1];
                  return (
                    <div key={category} className="category-stat-row">
                      <span className="category-name">{category}</span>
                      <span className="category-count">{count}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Admin;
