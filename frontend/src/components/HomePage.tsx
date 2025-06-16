import React from 'react';

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
        <h1>Welcome to GitHub OAuth Demo</h1>
        {user ? (
          <div className="user-welcome">
            <img 
              src={user.avatar_url} 
              alt="Avatar" 
              className="avatar-small"
            />
            <p>Hello, <strong>{user.name || user.login}</strong>!</p>
          </div>
        ) : (
          <p>Please log in to access your profile and repositories.</p>
        )}
      </div>
      
      <div className="features-section">
        <h2>Features</h2>
        <div className="features-grid">
          <div className="feature-card">
            <h3>User Profile</h3>
            <p>View your GitHub profile information, including bio, location, and social links.</p>
          </div>
          <div className="feature-card">
            <h3>Repositories</h3>
            <p>Browse all your GitHub repositories with detailed information and statistics.</p>
          </div>
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
