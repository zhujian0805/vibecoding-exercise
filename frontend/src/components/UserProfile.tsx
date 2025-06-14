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

  // Debug: Log user data to see what we're receiving
  useEffect(() => {
    if (user) {
      console.log('User data received in UserProfile:', user);
      console.log('Type of public_repos:', typeof user.public_repos, 'Value:', user.public_repos);
      console.log('Type of followers:', typeof user.followers, 'Value:', user.followers);
      console.log('Type of following:', typeof user.following, 'Value:', user.following);
      
      // Additional debug information
      console.log('User object keys:', Object.keys(user));
      console.log('All user values:', Object.entries(user));
    } else {
      console.log('No user data received in UserProfile');
    }
  }, [user]);

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

      <div className="stats-section">
        <h3 className="stats-title">GitHub Statistics</h3>
        <div className="stats">
          <a 
            href={`${user.html_url}?tab=repositories`} 
            target="_blank" 
            rel="noopener noreferrer"
            className="stat"
            title="View repositories on GitHub"
          >
            <strong>{(user.public_repos ?? 0).toLocaleString()}</strong>
            <span>Repositories</span>
          </a>
          <a 
            href={`${user.html_url}?tab=followers`} 
            target="_blank" 
            rel="noopener noreferrer"
            className="stat"
            title="View followers on GitHub"
          >
            <strong>{(user.followers ?? 0).toLocaleString()}</strong>
            <span>Followers</span>
          </a>
          <a 
            href={`${user.html_url}?tab=following`} 
            target="_blank" 
            rel="noopener noreferrer"
            className="stat"
            title="View following on GitHub"
          >
            <strong>{(user.following ?? 0).toLocaleString()}</strong>
            <span>Following</span>
          </a>
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
