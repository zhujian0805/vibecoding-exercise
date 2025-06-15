import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface User {
  login: string;
  id: number;
  avatar_url: string;
  html_url: string;
  type: string;
}

const API_BASE_URL = 'http://localhost:5000';

const Following: React.FC = () => {
  const [following, setFollowing] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchFollowing();
  }, []);

  const fetchFollowing = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/api/following`);
      setFollowing(response.data);
      setError(null);
    } catch (error) {
      console.error('Error fetching following:', error);
      setError('Failed to fetch following users');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading following users...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-container">
        <div className="error-container">
          <h2>Error</h2>
          <p>{error}</p>
          <button onClick={fetchFollowing} className="retry-btn">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="following-container">
        <h1>Following ({following.length})</h1>
        
        {following.length === 0 ? (
          <div className="empty-state">
            <p>You're not following anyone yet.</p>
          </div>
        ) : (
          <div className="users-grid">
            {following.map((user) => (
              <div key={user.id} className="user-card">
                <img 
                  src={user.avatar_url} 
                  alt={`${user.login}'s avatar`}
                  className="user-avatar"
                />
                <div className="user-info">
                  <h3 className="user-name">{user.login}</h3>
                  <p className="user-type">{user.type}</p>
                  <a 
                    href={user.html_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="user-link"
                  >
                    View Profile
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Following;
