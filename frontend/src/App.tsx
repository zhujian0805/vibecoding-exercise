import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

interface User {
  login: string;
  name: string;
  email: string;
  avatar_url: string;
  bio: string;
  location: string;
  company: string;
  blog: string;
  twitter_username: string;
  public_repos: number;
  followers: number;
  following: number;
  created_at: string;
  updated_at: string;
  html_url: string;
}

interface AuthState {
  authenticated: boolean;
  user: User | null;
  loading: boolean;
  error: string | null;
}

const API_BASE_URL = 'http://localhost:5000';

// Configure axios to include credentials with requests
axios.defaults.withCredentials = true;

function App() {
  const [authState, setAuthState] = useState<AuthState>({
    authenticated: false,
    user: null,
    loading: true,
    error: null
  });

  useEffect(() => {
    checkAuthStatus();
    handleOAuthCallback();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/user`);
      setAuthState({
        authenticated: true,
        user: response.data.user,
        loading: false,
        error: null
      });
    } catch (error) {
      setAuthState({
        authenticated: false,
        user: null,
        loading: false,
        error: null
      });
    }
  };

  const handleOAuthCallback = () => {
    const urlParams = new URLSearchParams(window.location.search);
    const error = urlParams.get('error');
    if (error) {
      setAuthState(prev => ({
        ...prev,
        error: `Login failed: ${error}`,
        loading: false
      }));
    }
  };

  const handleLogin = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/login`);
      window.location.href = response.data.auth_url;
    } catch (error) {
      setAuthState(prev => ({
        ...prev,
        error: 'Failed to initiate login'
      }));
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post(`${API_BASE_URL}/api/logout`);
      setAuthState({
        authenticated: false,
        user: null,
        loading: false,
        error: null
      });
    } catch (error) {
      setAuthState(prev => ({
        ...prev,
        error: 'Failed to logout'
      }));
    }
  };

  const fetchProfile = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/profile`);
      setAuthState(prev => ({
        ...prev,
        user: response.data
      }));
    } catch (error) {
      setAuthState(prev => ({
        ...prev,
        error: 'Failed to fetch profile'
      }));
    }
  };

  if (authState.loading) {
    return (
      <div className="App">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>GitHub OAuth Demo</h1>
        
        {authState.error && (
          <div className="error-message">
            {authState.error}
            <button 
              onClick={() => setAuthState(prev => ({ ...prev, error: null }))}
              className="error-close"
            >
              ×
            </button>
          </div>
        )}

        {!authState.authenticated ? (
          <div className="login-container">
            <div className="login-card">
              <h1 className="login-title">LLMBoddie Login</h1>
              
              <form className="login-form">
                <div className="form-group">
                  <label htmlFor="username">Username</label>
                  <input 
                    type="text" 
                    id="username" 
                    placeholder="Enter username"
                    disabled
                  />
                </div>
                
                <div className="form-group">
                  <label htmlFor="password">Password</label>
                  <input 
                    type="password" 
                    id="password" 
                    placeholder="Enter password"
                    disabled
                  />
                </div>
                
                <button type="button" className="login-btn" disabled>
                  Log In
                </button>
              </form>
              
              <div className="divider">
                <span>OR</span>
              </div>
              
              <button onClick={handleLogin} className="github-oauth-btn">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
                Login with GitHub (Simulated OAuth)
              </button>
              
              <div className="demo-hint">
                <p>Hint: Username is <code>user01</code></p>
                <p>Password is <code>password01</code></p>
              </div>
            </div>
          </div>
        ) : (
          <div className="profile-section">
            <div className="profile-header">
              <img 
                src={authState.user?.avatar_url} 
                alt="Avatar" 
                className="avatar"
              />
              <div className="profile-info">
                <h2>{authState.user?.name || authState.user?.login}</h2>
                <p className="username">@{authState.user?.login}</p>
                {authState.user?.bio && <p className="bio">{authState.user.bio}</p>}
              </div>
            </div>

            <div className="profile-details">
              <div className="detail-row">
                <strong>Email:</strong> {authState.user?.email || 'Not public'}
              </div>
              {authState.user?.location && (
                <div className="detail-row">
                  <strong>Location:</strong> {authState.user.location}
                </div>
              )}
              {authState.user?.company && (
                <div className="detail-row">
                  <strong>Company:</strong> {authState.user.company}
                </div>
              )}
              {authState.user?.blog && (
                <div className="detail-row">
                  <strong>Website:</strong> 
                  <a href={authState.user.blog} target="_blank" rel="noopener noreferrer">
                    {authState.user.blog}
                  </a>
                </div>
              )}
              {authState.user?.twitter_username && (
                <div className="detail-row">
                  <strong>Twitter:</strong> @{authState.user.twitter_username}
                </div>
              )}
            </div>

            <div className="stats">
              <div className="stat">
                <strong>{authState.user?.public_repos}</strong>
                <span>Repositories</span>
              </div>
              <div className="stat">
                <strong>{authState.user?.followers}</strong>
                <span>Followers</span>
              </div>
              <div className="stat">
                <strong>{authState.user?.following}</strong>
                <span>Following</span>
              </div>
            </div>

            <div className="actions">
              <button onClick={fetchProfile} className="refresh-btn">
                Refresh Profile
              </button>
              <a 
                href={authState.user?.html_url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="github-link-btn"
              >
                View on GitHub
              </a>
              <button onClick={handleLogout} className="logout-btn">
                Logout
              </button>
            </div>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
