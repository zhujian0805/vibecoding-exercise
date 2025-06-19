import React from 'react';
import { Link } from 'react-router-dom';

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
  total_repos: number;
  total_gists: number;
  followers: number;
  following: number;
  created_at: string;
  updated_at: string;
  html_url: string;
}

interface HomePageProps {
  user: User | null;
}

const HomePage: React.FC<HomePageProps> = ({ user }) => {
  return (
    <div className="home-page">
      <div className="welcome-section">
        <h1>Welcome to Vibecoding Exercise</h1>
        {user ? (
          <div className="user-welcome">
            <img 
              src={user.avatar_url} 
              alt="Avatar" 
              className="avatar-small"
            />
            <div className="user-info">
              <p>Hello, <strong>{user.name || user.login}</strong>!</p>
              <div className="user-stats">
                <span className="stat-item">
                  <strong>{user.total_repos || user.public_repos || 0}</strong> repositories
                </span>
                <span className="stat-item">
                  <strong>{user.total_gists || 0}</strong> gists
                </span>
                <span className="stat-item">
                  <strong>{user.followers || 0}</strong> followers
                </span>
                <span className="stat-item">
                  <strong>{user.following || 0}</strong> following
                </span>
              </div>
            </div>
          </div>
        ) : (
          <p>Please log in to access your profile and repositories.</p>
        )}
      </div>
      
      <div className="features-section">
        <h2>Features</h2>
        <div className="features-grid">
          <Link to="/profile" className="feature-card">
            <h3>Profile</h3>
            <p>View your GitHub profile information, including bio, location, and social links.</p>
          </Link>
          <Link to="/repositories" className="feature-card">
            <h3>Repositories</h3>
            <p>Browse all your GitHub repositories with detailed information and statistics.</p>
          </Link>
          <Link to="/gists" className="feature-card">
            <h3>Gists</h3>
            <p>View and manage your GitHub gists with search and sorting capabilities.</p>
          </Link>
          <Link to="/following" className="feature-card">
            <h3>Following</h3>
            <p>See who you're following on GitHub and explore their profiles.</p>
          </Link>
          <Link to="/followers" className="feature-card">
            <h3>Followers</h3>
            <p>View your GitHub followers and see who's interested in your work.</p>
          </Link>
          <div className="feature-card">
            <h3>OAuth Flow</h3>
            <p>Secure authentication using GitHub's OAuth 2.0 flow.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
