import { CheckCircle, Clock, Flag, ArrowRight, Check } from 'lucide-react';
import { format } from 'date-fns';
import { useNavigate } from 'react-router-dom';

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

const TaskCard = ({ task, onToggle, showScore, mode = 'dashboard' }) => {
  const navigate = useNavigate();

  const handleGoToTasks = () => {
    navigate('/tasks');
  };

  return (
    <div className={`task-card ${task.is_completed ? 'completed' : ''}`}>
      <div className="task-content">
        <div className="task-header">
          <h4 className="task-title">
            {task.is_completed && <CheckCircle size={16} className="completed-icon" />}
            {task.title}
          </h4>
          {showScore && task.score !== undefined && (
            <span className="task-score" title="Recommendation score">
              {Math.round(task.score)}%
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
      
      <div className="task-hover-actions">
        {mode === 'tasks' ? (
          <button 
            className={`action-btn ${task.is_completed ? 'undo' : 'complete'}`}
            onClick={() => onToggle(task)}
          >
            <Check size={16} />
            {task.is_completed ? 'Undo' : 'Complete'}
          </button>
        ) : (
          <button 
            className="action-btn goto"
            onClick={handleGoToTasks}
          >
            <ArrowRight size={16} />
            Go to Todo List
          </button>
        )}
      </div>
    </div>
  );
};

export default TaskCard;
