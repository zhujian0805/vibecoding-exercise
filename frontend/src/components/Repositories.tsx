import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Repository {
  id: number;
  name: string;
  full_name: string;
  description: string;
  private: boolean;
  html_url: string;
  clone_url: string;
  ssh_url: string;
  language: string;
  stargazers_count: number;
  watchers_count: number;
  forks_count: number;
  size: number;
  default_branch: string;
  created_at: string;
  updated_at: string;
  pushed_at: string;
  archived: boolean;
  disabled: boolean;
  fork: boolean;
  topics: string[];
  visibility: string;
}

interface RepositoriesResponse {
  repositories: Repository[];
  page: number;
  per_page: number;
  total_count: number;
}

const API_BASE_URL = 'http://localhost:5000';

const Repositories: React.FC = () => {
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [sortBy, setSortBy] = useState('updated');

  useEffect(() => {
    fetchRepositories();
  }, [page, sortBy]);

  const fetchRepositories = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get<RepositoriesResponse>(
        `${API_BASE_URL}/api/repositories?page=${page}&per_page=30&sort=${sortBy}`,
        { withCredentials: true }
      );
      setRepositories(response.data.repositories);
    } catch (err) {
      setError('Failed to fetch repositories');
      console.error('Error fetching repositories:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getLanguageColor = (language: string) => {
    const colors: { [key: string]: string } = {
      JavaScript: '#f1e05a',
      TypeScript: '#2b7489',
      Python: '#3572A5',
      Java: '#b07219',
      'C++': '#f34b7d',
      C: '#555555',
      'C#': '#239120',
      PHP: '#4F5D95',
      Go: '#00ADD8',
      Rust: '#dea584',
      Swift: '#ffac45',
      Kotlin: '#F18E33',
      Ruby: '#701516',
      HTML: '#e34c26',
      CSS: '#1572B6',
      Shell: '#89e051',
    };
    return colors[language] || '#586069';
  };

  if (loading) {
    return (
      <div className="repositories">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading repositories...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="repositories">
        <div className="error-message">
          {error}
          <button onClick={fetchRepositories} className="retry-btn">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="repositories">
      <div className="repositories-header">
        <h1>My Repositories</h1>
        <div className="repositories-controls">
          <label>
            Sort by:
            <select 
              value={sortBy} 
              onChange={(e) => setSortBy(e.target.value)}
              className="sort-select"
            >
              <option value="updated">Recently Updated</option>
              <option value="created">Recently Created</option>
              <option value="pushed">Recently Pushed</option>
              <option value="full_name">Name</option>
            </select>
          </label>
        </div>
      </div>

      <div className="repositories-grid">
        {repositories.length === 0 ? (
          <div className="no-repositories">
            <p>No repositories found.</p>
          </div>
        ) : (
          repositories.map((repo) => (
            <div key={repo.id} className="repository-card">
              <div className="repo-header">
                <h3>
                  <a 
                    href={repo.html_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="repo-name"
                  >
                    {repo.name}
                  </a>
                  {repo.private && <span className="private-badge">Private</span>}
                  {repo.fork && <span className="fork-badge">Fork</span>}
                </h3>
              </div>
              
              {repo.description && (
                <p className="repo-description">{repo.description}</p>
              )}
              
              <div className="repo-stats">
                {repo.language && (
                  <span className="language">
                    <span 
                      className="language-color" 
                      style={{ backgroundColor: getLanguageColor(repo.language) }}
                    ></span>
                    {repo.language}
                  </span>
                )}
                <span className="stat">
                  ⭐ {repo.stargazers_count}
                </span>
                <span className="stat">
                  🍴 {repo.forks_count}
                </span>
                {repo.size > 0 && (
                  <span className="stat">
                    📦 {Math.round(repo.size / 1024)} KB
                  </span>
                )}
              </div>
              
              {repo.topics && repo.topics.length > 0 && (
                <div className="repo-topics">
                  {repo.topics.slice(0, 3).map((topic) => (
                    <span key={topic} className="topic-tag">
                      {topic}
                    </span>
                  ))}
                  {repo.topics.length > 3 && (
                    <span className="topic-tag more">
                      +{repo.topics.length - 3} more
                    </span>
                  )}
                </div>
              )}
              
              <div className="repo-footer">
                <span className="updated-date">
                  Updated {formatDate(repo.updated_at)}
                </span>
              </div>
            </div>
          ))
        )}
      </div>

      {repositories.length > 0 && (
        <div className="pagination">
          <button 
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="page-btn"
          >
            Previous
          </button>
          <span className="page-info">Page {page}</span>
          <button 
            onClick={() => setPage(p => p + 1)}
            disabled={repositories.length < 30}
            className="page-btn"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

export default Repositories;
