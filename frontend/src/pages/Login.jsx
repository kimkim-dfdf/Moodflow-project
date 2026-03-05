import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Login() {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const { login, signup } = useAuth();
  const navigate = useNavigate();

  function handleLoginSubmit(e) {
    e.preventDefault();
    setError('');
    setSuccess('');
    
    login(email, password)
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

  function handleSignUpSubmit(e) {
    e.preventDefault();
    setError('');
    setSuccess('');

    // 비밀번호 확인
    if (password !== passwordConfirm) {
      setError('Passwords do not match');
      return;
    }

    signup(email, username, password)
      .then(function() {
        navigate('/dashboard');
      })
      .catch(function(err) {
        if (err.response && err.response.data) {
          setError(err.response.data.error);
        } else {
          setError('Sign up failed');
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

        {!isSignUp ? (
          <form onSubmit={handleLoginSubmit} className="auth-form">
            <h2>Welcome Back</h2>
            
            {error && <div className="error-message">{error}</div>}

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

            <div className="auth-toggle">
              <p>Don't have an account? 
                <button 
                  type="button" 
                  onClick={function() { 
                    setIsSignUp(true);
                    setEmail('');
                    setPassword('');
                    setError('');
                  }}
                  className="link-button"
                >
                  Sign Up
                </button>
              </p>
            </div>

            <div className="demo-accounts">
              <p>Demo Accounts:</p>
              <p>seven@gmail.com / elly@gmail.com / nicole@gmail.com</p>
              <p>Password: ekdus123</p>
            </div>
          </form>
        ) : (
          <form onSubmit={handleSignUpSubmit} className="auth-form">
            <h2>Create Account</h2>
            
            {error && <div className="error-message">{error}</div>}
            {success && <div className="success-message">{success}</div>}

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
              <label>Username</label>
              <input
                type="text"
                value={username}
                onChange={function(e) { setUsername(e.target.value); }}
                placeholder="Choose a username"
                minLength="2"
                required
              />
            </div>

            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                value={password}
                onChange={function(e) { setPassword(e.target.value); }}
                placeholder="At least 6 characters"
                minLength="6"
                required
              />
            </div>

            <div className="form-group">
              <label>Confirm Password</label>
              <input
                type="password"
                value={passwordConfirm}
                onChange={function(e) { setPasswordConfirm(e.target.value); }}
                placeholder="Confirm your password"
                minLength="6"
                required
              />
            </div>

            <button type="submit" className="btn-primary">
              Sign Up
            </button>

            <div className="auth-toggle">
              <p>Already have an account? 
                <button 
                  type="button" 
                  onClick={function() { 
                    setIsSignUp(false);
                    setUsername('');
                    setPasswordConfirm('');
                    setError('');
                  }}
                  className="link-button"
                >
                  Sign In
                </button>
              </p>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

export default Login;
