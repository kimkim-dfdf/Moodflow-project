import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';
import { User, Mail, Save, TrendingUp } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const EMOTION_COLORS = {
  'Happy': '#FFD93D',
  'Sad': '#6B7FD7',
  'Tired': '#A8A8A8',
  'Angry': '#FF6B6B',
  'Stressed': '#FF9F43',
  'Neutral': '#95A5A6'
};

const Profile = () => {
  const { user, setUser } = useAuth();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [emotionStats, setEmotionStats] = useState(null);

  const [formData, setFormData] = useState({
    username: user?.username || ''
  });

  useEffect(() => {
    fetchEmotionData();
  }, []);

  useEffect(() => {
    if (user) {
      setFormData({
        username: user.username || ''
      });
    }
  }, [user]);

  const fetchEmotionData = async () => {
    try {
      const response = await api.get('/emotions/statistics', { params: { days: 30 } });
      setEmotionStats(response.data);
    } catch (error) {
      console.error('Failed to fetch emotion data:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const response = await api.put('/user/profile', formData);
      setUser(response.data);
      setMessage('Profile updated successfully!');
    } catch (error) {
      setMessage(error.response?.data?.error || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const pieData = emotionStats?.counts 
    ? Object.entries(emotionStats.counts).map(([name, value]) => ({
        name,
        value,
        color: EMOTION_COLORS[name] || '#95A5A6'
      }))
    : [];

  return (
    <div className="profile-page">
      <header className="page-header">
        <h1>My Profile</h1>
      </header>

      <div className="profile-grid">
        <section className="card profile-info">
          <h2><User size={20} /> Account Settings</h2>
          
          <form onSubmit={handleSubmit}>
            {message && (
              <div className={`message ${message.includes('success') ? 'success' : 'error'}`}>
                {message}
              </div>
            )}

            <div className="form-group">
              <label htmlFor="username">
                <User size={16} /> Username
              </label>
              <input
                type="text"
                id="username"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                placeholder="Your username"
              />
            </div>

            <div className="form-group">
              <label><Mail size={16} /> Email</label>
              <input
                type="email"
                value={user?.email || ''}
                disabled
                className="disabled"
              />
              <small>Email cannot be changed</small>
            </div>

            <button type="submit" className="btn-primary" disabled={loading}>
              <Save size={18} />
              {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </form>
        </section>

        <section className="card emotion-history">
          <h2><TrendingUp size={20} /> Emotion History</h2>
          
          {emotionStats && pieData.length > 0 ? (
            <>
              <div className="stats-overview">
                <div className="stat-item">
                  <span className="stat-value">{emotionStats.total_entries}</span>
                  <span className="stat-label">Days Tracked</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">{emotionStats.dominant_emotion}</span>
                  <span className="stat-label">Most Common Mood</span>
                </div>
              </div>

              <div className="chart-container">
                <h3>Mood Distribution (Last 30 Days)</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={2}
                      dataKey="value"
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>

            </>
          ) : (
            <div className="empty-state">
              <p>No emotion data yet. Start tracking your daily mood to see insights!</p>
            </div>
          )}
        </section>

      </div>
    </div>
  );
};

export default Profile;
