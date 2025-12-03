import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Login() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  function handleSubmit(e) {
    e.preventDefault();
    setError('');
    
    login(email, password, name)
      .then(function() {
        navigate('/dashboard');
      })
      .catch(function(err) {
        if (err.response && err.response.data) {
          setError(err.response.data.error);
        } else {
          setError('Login failed');
        }
      });
  }

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <h1>MoodFlow</h1>
          <p>Track your emotions, boost your productivity</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <h2>Welcome Back</h2>
          
          {error && <div className="error-message">{error}</div>}

          <div className="form-group">
            <label>Name</label>
            <input
              type="text"
              value={name}
              onChange={function(e) { setName(e.target.value); }}
              placeholder="Enter your name"
              required
            />
          </div>

          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={function(e) { setEmail(e.target.value); }}
              placeholder="Enter your email"
              required
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={function(e) { setPassword(e.target.value); }}
              placeholder="Enter your password"
              required
            />
          </div>

          <button type="submit" className="btn-primary">
            Sign In
          </button>

          <div className="demo-accounts">
            <p>Demo Accounts:</p>
            <p>seven@gmail.com / elly@gmail.com / nicole@gmail.com</p>
            <p>Password: ekdus123</p>
          </div>
        </form>
      </div>
    </div>
  );
}

export default Login;
