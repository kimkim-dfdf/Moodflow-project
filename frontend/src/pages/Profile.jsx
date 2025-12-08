import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';
import { Mail, Save, TrendingUp } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

function Profile() {
  const { user, setUser } = useAuth();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [stats, setStats] = useState(null);
  const [username, setUsername] = useState(user ? user.username : '');

  useEffect(function() {
    api.get('/emotions/statistics', { params: { days: 30 } }).then(function(res) { setStats(res.data); });
  }, []);

  useEffect(function() {
    if (user) setUsername(user.username);
  }, [user]);

  function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    api.put('/user/profile', { username: username }).then(function(res) {
      setUser(res.data);
      setMessage('Saved!');
      setLoading(false);
    }).catch(function(err) {
      if (err.response && err.response.data) setMessage(err.response.data.error);
      else setMessage('Failed');
      setLoading(false);
    });
  }

  var pieData = [];
  var colors = { Happy: '#FFD93D', Sad: '#6B7FD7', Tired: '#A8A8A8', Angry: '#FF6B6B', Stressed: '#FF9F43', Neutral: '#95A5A6' };
  if (stats && stats.counts) {
    for (var name in stats.counts) {
      pieData.push({ name: name, value: stats.counts[name], color: colors[name] || '#95A5A6' });
    }
  }

  return (
    <div className="profile-page">
      <header className="page-header"><h1>My Profile</h1></header>

      <div className="profile-grid">
        <section className="card">
          <h2>Settings</h2>
          <form onSubmit={handleSubmit}>
            {message && <div className="error-message">{message}</div>}
            <div className="form-group">
              <label>Username</label>
              <input type="text" value={username} onChange={function(e) { setUsername(e.target.value); }} />
            </div>
            <div className="form-group">
              <label><Mail size={16} /> Email</label>
              <input type="email" value={user ? user.email : ''} disabled className="disabled" />
              <small>Cannot change</small>
            </div>
            <button type="submit" className="btn-primary" disabled={loading}><Save size={18} /> {loading ? 'Saving...' : 'Save'}</button>
          </form>
        </section>

        <section className="card">
          <h2><TrendingUp size={20} /> Mood History</h2>
          {pieData.length > 0 ? (
            <>
              <div className="stat-grid">
                <div className="stat-item"><span className="stat-value">{stats.total_entries}</span><span className="stat-label">Days</span></div>
                <div className="stat-item"><span className="stat-value">{stats.dominant_emotion}</span><span className="stat-label">Top Mood</span></div>
              </div>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={70} dataKey="value">
                    {pieData.map(function(e, i) { return <Cell key={i} fill={e.color} />; })}
                  </Pie>
                  <Tooltip /><Legend />
                </PieChart>
              </ResponsiveContainer>
            </>
          ) : (
            <p className="empty-state">No data yet</p>
          )}
        </section>
      </div>
    </div>
  );
}

export default Profile;
