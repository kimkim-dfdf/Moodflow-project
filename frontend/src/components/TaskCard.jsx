import { CheckCircle, Circle, Clock, Flag } from 'lucide-react';
import { format } from 'date-fns';

const priorityColors = {
  High: '#ef4444',
  Medium: '#f59e0b',
  Low: '#22c55e'
};

const categoryColors = {
  Work: '#6366f1',
  Study: '#8b5cf6',
  Health: '#10b981',
  Personal: '#f97316'
};

const getMatchLevel = (score) => {
  if (score >= 90) return { stars: '⭐⭐⭐⭐⭐', text: 'Perfect!' };
  if (score >= 70) return { stars: '⭐⭐⭐⭐', text: 'Great!' };
  if (score >= 50) return { stars: '⭐⭐⭐', text: 'Good' };
  if (score >= 30) return { stars: '⭐⭐', text: 'Try it' };
  return { stars: '⭐', text: 'Later?' };
};

const TaskCard = ({ task, onToggle, onEdit, showScore }) => {
  const matchLevel = showScore && task.score !== undefined ? getMatchLevel(task.score) : null;

  return (
    <div className={`task-card ${task.is_completed ? 'completed' : ''}`}>
      <div className="task-header">
        <button className="toggle-btn" onClick={() => onToggle(task)}>
          {task.is_completed ? (
            <CheckCircle size={20} className="checked" />
          ) : (
            <Circle size={20} />
          )}
        </button>
        <h4 className="task-title">{task.title}</h4>
        {matchLevel && (
          <span className="task-match" title={matchLevel.text}>
            {matchLevel.stars}
          </span>
        )}
      </div>
      
      {task.description && (
        <p className="task-description">{task.description}</p>
      )}
      
      <div className="task-meta">
        <span 
          className="task-category"
          style={{ backgroundColor: categoryColors[task.category] || '#6366f1' }}
        >
          {task.category}
        </span>
        <span 
          className="task-priority"
          style={{ color: priorityColors[task.priority] || '#f59e0b' }}
        >
          <Flag size={14} />
          {task.priority}
        </span>
        {task.due_date && (
          <span className="task-due">
            <Clock size={14} />
            {format(new Date(task.due_date), 'MMM d')}
          </span>
        )}
      </div>
    </div>
  );
};

export default TaskCard;
