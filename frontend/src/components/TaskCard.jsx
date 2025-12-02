import { CheckCircle, Clock, Flag, ArrowRight, Check } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

function TaskCard(props) {
  var task = props.task;
  var onToggle = props.onToggle;
  var showScore = props.showScore;
  var mode = props.mode;
  
  const navigate = useNavigate();

  function getCategoryColor(category) {
    if (category === 'Work') return '#6366f1';
    if (category === 'Study') return '#8b5cf6';
    if (category === 'Health') return '#10b981';
    if (category === 'Personal') return '#f97316';
    return '#6366f1';
  }

  function getPriorityColor(priority) {
    if (priority === 'High') return '#ef4444';
    if (priority === 'Medium') return '#f59e0b';
    if (priority === 'Low') return '#22c55e';
    return '#f59e0b';
  }

  return (
    <div className={'task-card ' + (task.is_completed ? 'completed' : '')}>
      <div className="task-content">
        <div className="task-header">
          <h4 className="task-title">
            {task.is_completed && <CheckCircle size={16} className="completed-icon" />}
            {task.title}
          </h4>
          {showScore && task.score !== undefined && <span className="task-score">{Math.round(task.score)}%</span>}
        </div>
        {task.description && <p className="task-description">{task.description}</p>}
        <div className="task-meta">
          <span className="task-category" style={{ backgroundColor: getCategoryColor(task.category) }}>{task.category}</span>
          <span className="task-priority" style={{ color: getPriorityColor(task.priority) }}><Flag size={14} />{task.priority}</span>
          {task.due_time && <span className="task-due"><Clock size={14} />{task.due_time}</span>}
        </div>
      </div>
      
      <div className="task-hover-actions">
        {mode === 'tasks' ? (
          <button className={'action-btn ' + (task.is_completed ? 'undo' : 'complete')} onClick={function() { onToggle(task); }}>
            <Check size={16} />{task.is_completed ? 'Undo' : 'Complete'}
          </button>
        ) : (
          <button className="action-btn goto" onClick={function() { navigate('/tasks'); }}>
            <ArrowRight size={16} />Go to Todo List
          </button>
        )}
      </div>
    </div>
  );
}

export default TaskCard;
