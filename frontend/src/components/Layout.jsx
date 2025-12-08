import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LayoutDashboard, CheckSquare, Calendar, BookOpen, User, LogOut, Shield } from 'lucide-react';

const Layout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/tasks', icon: CheckSquare, label: 'Tasks' },
    { path: '/calendar', icon: Calendar, label: 'Calendar' },
    { path: '/books', icon: BookOpen, label: 'Books' },
    { path: '/profile', icon: User, label: 'Profile' },
    ...(user?.is_admin ? [{ path: '/admin', icon: Shield, label: 'Admin' }] : []),
  ];

  return (
    <div className="app-container">
      <nav className="sidebar">
        <div className="sidebar-header">
          <h1 className="logo">MoodFlow</h1>
        </div>
        
        <ul className="nav-menu">
          {navItems.map((item) => (
            <li key={item.path}>
              <NavLink to={item.path} className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                <item.icon size={20} />
                <span>{item.label}</span>
              </NavLink>
            </li>
          ))}
        </ul>

        <div className="sidebar-footer">
          <div className="user-info">
            <div className="user-avatar">{user?.username?.[0]?.toUpperCase() || 'U'}</div>
            <span className="user-name">{user?.username || 'User'}</span>
          </div>
          <button onClick={handleLogout} className="logout-btn">
            <LogOut size={18} />
          </button>
        </div>
      </nav>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
