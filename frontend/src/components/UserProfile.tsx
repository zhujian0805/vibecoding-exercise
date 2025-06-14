import React, { useState, useEffect } from 'react';
import axios from 'axios';

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

interface UserProfileProps {
  user: User | null;
  onRefreshProfile: () => void;
}

const UserProfile: React.FC<UserProfileProps> = ({ user, onRefreshProfile }) => {
  const [loading, setLoading] = useState(false);

  const handleRefresh = async () => {
    setLoading(true);
    await onRefreshProfile();
    setLoading(false);
  };

  if (!user) {
    return (
      <div className="user-profile">
        <div className="error-message">
          No user data available. Please try refreshing or logging in again.
        </div>
      </div>
    );
  }

  return (
    <div className="user-profile">
      <div className="profile-header">
        <img 
          src={user.avatar_url} 
          alt="Avatar" 
          className="avatar-large"
        />
        <div className="profile-info">
          <h1>{user.name || user.login}</h1>
          <p className="username">@{user.login}</p>
          {user.bio && <p className="bio">{user.bio}</p>}
        </div>
      </div>

      <div className="profile-details">
        <div className="detail-row">
          <strong>Email:</strong> {user.email || 'Not public'}
        </div>
        {user.location && (
          <div className="detail-row">
            <strong>Location:</strong> {user.location}
          </div>
        )}
        {user.company && (
          <div className="detail-row">
            <strong>Company:</strong> {user.company}
          </div>
        )}
        {user.blog && (
          <div className="detail-row">
            <strong>Website:</strong> 
            <a href={user.blog} target="_blank" rel="noopener noreferrer">
              {user.blog}
            </a>
          </div>
        )}
        {user.twitter_username && (
          <div className="detail-row">
            <strong>Twitter:</strong> 
            <a 
              href={`https://twitter.com/${user.twitter_username}`} 
              target="_blank" 
              rel="noopener noreferrer"
            >
              @{user.twitter_username}
            </a>
          </div>
        )}
      </div>

      <div className="stats">
        <div className="stat">
          <strong>{user.public_repos}</strong>
          <span>Repositories</span>
        </div>
        <div className="stat">
          <strong>{user.followers}</strong>
          <span>Followers</span>
        </div>
        <div className="stat">
          <strong>{user.following}</strong>
          <span>Following</span>
        </div>
      </div>

      <div className="profile-actions">
        <button 
          onClick={handleRefresh} 
          className="refresh-btn"
          disabled={loading}
        >
          {loading ? 'Refreshing...' : 'Refresh Profile'}
        </button>
        <a 
          href={user.html_url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="github-link-btn"
        >
          View on GitHub
        </a>
      </div>
    </div>
  );
};

export default UserProfile;
