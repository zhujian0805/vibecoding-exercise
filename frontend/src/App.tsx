import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import './App.css';

// Components
import Navigation from './components/Navigation';
import HomePage from './components/HomePage';
import LoginPage from './components/LoginPage';
import UserProfile from './components/UserProfile';
import Repositories from './components/Repositories';
import ProtectedRoute from './components/ProtectedRoute';

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

  const clearError = () => {
    setAuthState(prev => ({ ...prev, error: null }));
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
      <Router>
        <Navigation 
          isAuthenticated={authState.authenticated}
          user={authState.user}
          onLogout={handleLogout}
        />
        
        <main className="main-content">
          <Routes>
            <Route 
              path="/" 
              element={
                authState.authenticated ? (
                  <HomePage user={authState.user} />
                ) : (
                  <Navigate to="/login" replace />
                )
              } 
            />
            <Route 
              path="/login" 
              element={
                authState.authenticated ? (
                  <Navigate to="/" replace />
                ) : (
                  <LoginPage 
                    onLogin={handleLogin}
                    error={authState.error}
                    onClearError={clearError}
                  />
                )
              } 
            />
            <Route 
              path="/profile" 
              element={
                <ProtectedRoute isAuthenticated={authState.authenticated}>
                  <UserProfile 
                    user={authState.user}
                    onRefreshProfile={fetchProfile}
                  />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/repositories" 
              element={
                <ProtectedRoute isAuthenticated={authState.authenticated}>
                  <Repositories />
                </ProtectedRoute>
              } 
            />
          </Routes>
        </main>
      </Router>
    </div>
  );
}

export default App;
