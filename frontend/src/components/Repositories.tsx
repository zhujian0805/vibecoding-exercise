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
  const [copyMessage, setCopyMessage] = useState<string | null>(null);

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

  const handleCopyCloneUrl = async (cloneUrl: string, repoName: string) => {
    try {
      await navigator.clipboard.writeText(cloneUrl);
      setCopyMessage(`Clone URL copied for ${repoName}!`);
      setTimeout(() => setCopyMessage(null), 3000);
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
      setCopyMessage('Failed to copy clone URL');
      setTimeout(() => setCopyMessage(null), 3000);
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
      {copyMessage && (
        <div className="copy-message">
          {copyMessage}
        </div>
      )}
      
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

      {repositories.length === 0 ? (
        <div className="no-repositories">
          <p>No repositories found.</p>
        </div>
      ) : (
        <div className="repositories-table-container">
          <table className="repositories-table">
            <thead>
              <tr>
                <th>Repository</th>
                <th>Description</th>
                <th>Language</th>
                <th>Stars</th>
                <th>Forks</th>
                <th>Size</th>
                <th>Updated</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {repositories.map((repo) => (
                <tr key={repo.id}>
                  <td className="repo-name-cell">
                    <div className="repo-name-container">
                      <a 
                        href={repo.html_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="repo-name-link"
                      >
                        {repo.name}
                      </a>
                      <div className="repo-badges">
                        {repo.private && <span className="badge private">Private</span>}
                        {repo.fork && <span className="badge fork">Fork</span>}
                        {repo.archived && <span className="badge archived">Archived</span>}
                      </div>
                    </div>
                  </td>
                  
                  <td className="repo-description-cell">
                    <div className="description-content">
                      {repo.description ? (
                        <span className="description-text">{repo.description}</span>
                      ) : (
                        <span className="no-description">No description</span>
                      )}
                      {repo.topics && repo.topics.length > 0 && (
                        <div className="topic-tags">
                          {repo.topics.slice(0, 2).map((topic) => (
                            <span key={topic} className="topic-tag">
                              {topic}
                            </span>
                          ))}
                          {repo.topics.length > 2 && (
                            <span className="topic-tag more">
                              +{repo.topics.length - 2}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  </td>
                  
                  <td className="language-cell">
                    {repo.language && (
                      <div className="language-info">
                        <span 
                          className="language-color" 
                          style={{ backgroundColor: getLanguageColor(repo.language) }}
                        ></span>
                        <span className="language-name">{repo.language}</span>
                      </div>
                    )}
                  </td>
                  
                  <td className="stars-cell">
                    <span className="stat-value">⭐ {repo.stargazers_count}</span>
                  </td>
                  
                  <td className="forks-cell">
                    <span className="stat-value">🍴 {repo.forks_count}</span>
                  </td>
                  
                  <td className="size-cell">
                    {repo.size > 0 ? (
                      <span className="stat-value">{Math.round(repo.size / 1024)} KB</span>
                    ) : (
                      <span className="no-data">—</span>
                    )}
                  </td>
                  
                  <td className="updated-cell">
                    <span className="updated-date">{formatDate(repo.updated_at)}</span>
                  </td>
                  
                  <td className="actions-cell">
                    <div className="repo-actions">
                      <a 
                        href={repo.html_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="action-btn view-btn"
                        title="View on GitHub"
                      >
                        View
                      </a>
                      <button 
                        onClick={() => handleCopyCloneUrl(repo.clone_url, repo.name)}
                        className="action-btn clone-btn"
                        title="Copy clone URL"
                      >
                        Clone
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

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
