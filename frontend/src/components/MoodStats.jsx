import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const EMOTION_COLORS = {
  'Happy': '#FFD93D',
  'Sad': '#6B7FD7',
  'Tired': '#A8A8A8',
  'Angry': '#FF6B6B',
  'Stressed': '#FF9F43',
  'Neutral': '#95A5A6'
};

const MoodStats = ({ stats }) => {
  if (!stats || !stats.counts || Object.keys(stats.counts).length === 0) {
    return (
      <div className="mood-stats empty">
        <p>No mood data yet. Start tracking your emotions!</p>
      </div>
    );
  }

  const data = Object.entries(stats.counts).map(([name, value]) => ({
    name,
    value,
    color: EMOTION_COLORS[name] || '#95A5A6'
  }));

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
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
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
};

export default MoodStats;
