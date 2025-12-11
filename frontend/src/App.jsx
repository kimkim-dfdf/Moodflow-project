import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { DateProvider } from './context/DateContext';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Tasks from './pages/Tasks';
import Calendar from './pages/Calendar';
import Books from './pages/Books';
import Music from './pages/Music';
import Challenge from './pages/Challenge';
import Profile from './pages/Profile';
import Admin from './pages/Admin';
import './index.css';

const PrivateRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <div className="loading-screen">Loading...</div>;
  }
  
  return user ? children : <Navigate to="/login" />;
};

const PublicRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <div className="loading-screen">Loading...</div>;
  }
  
  if (user) {
    if (user.is_admin) {
      return <Navigate to="/admin" />;
    }
    return <Navigate to="/dashboard" />;
  }
  
  return children;
};

const DefaultRedirect = () => {
  const { user } = useAuth();
  if (user && user.is_admin) {
    return <Navigate to="/admin" />;
  }
  return <Navigate to="/dashboard" />;
};

function App() {
  return (
    <AuthProvider>
      <DateProvider>
        <Router>
          <Routes>
          <Route path="/login" element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          } />
          <Route path="/" element={
            <PrivateRoute>
              <Layout />
            </PrivateRoute>
          }>
            <Route index element={<DefaultRedirect />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="tasks" element={<Tasks />} />
            <Route path="calendar" element={<Calendar />} />
            <Route path="books" element={<Books />} />
            <Route path="music" element={<Music />} />
            <Route path="challenge" element={<Challenge />} />
            <Route path="profile" element={<Profile />} />
            <Route path="admin" element={<Admin />} />
          </Route>
          <Route path="*" element={<DefaultRedirect />} />
          </Routes>
        </Router>
      </DateProvider>
    </AuthProvider>
  );
}

export default App;
