import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LayoutDashboard, CheckSquare, Calendar, BookOpen, User, LogOut, Settings } from 'lucide-react';

function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout().then(function() {
      navigate('/login');
    });
  }

  function getFirstLetter() {
    if (user && user.username) {
      return user.username[0].toUpperCase();
    }
    return 'U';
  }

  function getNavClass(isActive) {
    if (isActive) return 'nav-link active';
    return 'nav-link';
  }

  return (
    <div className="app-container">
      <nav className="sidebar">
        <div className="sidebar-header">
          <h1 className="logo">MoodFlow</h1>
        </div>
        
        <ul className="nav-menu">
          {user && user.is_admin ? (
            <li><NavLink to="/admin" className={function(p) { return getNavClass(p.isActive); }}><Settings size={20} /><span>Admin</span></NavLink></li>
          ) : (
            <>
              <li><NavLink to="/dashboard" className={function(p) { return getNavClass(p.isActive); }}><LayoutDashboard size={20} /><span>Dashboard</span></NavLink></li>
              <li><NavLink to="/tasks" className={function(p) { return getNavClass(p.isActive); }}><CheckSquare size={20} /><span>Tasks</span></NavLink></li>
              <li><NavLink to="/calendar" className={function(p) { return getNavClass(p.isActive); }}><Calendar size={20} /><span>Calendar</span></NavLink></li>
              <li><NavLink to="/books" className={function(p) { return getNavClass(p.isActive); }}><BookOpen size={20} /><span>Books</span></NavLink></li>
              <li><NavLink to="/profile" className={function(p) { return getNavClass(p.isActive); }}><User size={20} /><span>Profile</span></NavLink></li>
            </>
          )}
        </ul>

        <div className="sidebar-footer">
          <div className="user-info">
            <div className="user-avatar">{getFirstLetter()}</div>
            <span className="user-name">{user ? user.username : 'User'}</span>
          </div>
          <button onClick={handleLogout} className="logout-btn"><LogOut size={18} /></button>
        </div>
      </nav>

      <main className="main-content"><Outlet /></main>
    </div>
  );
}

export default Layout;
