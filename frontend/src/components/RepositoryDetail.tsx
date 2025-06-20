import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
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
  git_url: string;
  svn_url: string;
  homepage: string;
  language: string;
  stargazers_count: number;
  watchers_count: number;
  forks_count: number;
  open_issues_count: number;
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
  license: {
    key: string;
    name: string;
    spdx_id: string;
    url: string;
  } | null;
  owner: {
    login: string;
    avatar_url: string;
    html_url: string;
  };
}

interface RepositoryDetailProps {}

const API_BASE_URL = 'http://localhost:5000';

const RepositoryDetail: React.FC<RepositoryDetailProps> = () => {
  const { owner, repo } = useParams<{ owner: string; repo: string }>();
  const navigate = useNavigate();
  const [repository, setRepository] = useState<Repository | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copyMessage, setCopyMessage] = useState<string | null>(null);

  useEffect(() => {
    const fetchRepository = async () => {
      if (!owner || !repo) {
        setError('Invalid repository parameters');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        
        console.log(`[DEBUG] Fetching repository details for ${owner}/${repo}`);
        
        const response = await axios.get(
          `${API_BASE_URL}/api/repositories/${owner}/${repo}`,
          { withCredentials: true }
        );
        
        console.log(`[DEBUG] Repository details fetched successfully:`, response.data);
        setRepository(response.data);
      } catch (err: any) {
        console.error('Error fetching repository:', err);
        if (err.response?.status === 401) {
          setError('Authentication required. Please log in again.');
        } else if (err.response?.status === 404) {
          setError('Repository not found. It may be private or does not exist.');
        } else if (err.response?.status === 403) {
          setError('Access denied. You may not have permission to view this repository.');
        } else {
          setError(err.response?.data?.error || 'Failed to load repository details. Please try again.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchRepository();
  }, [owner, repo]);

  const copyToClipboard = async (text: string, type: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopyMessage(`${type} copied to clipboard!`);
      setTimeout(() => setCopyMessage(null), 3000);
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
      setCopyMessage('Failed to copy to clipboard');
      setTimeout(() => setCopyMessage(null), 3000);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const getLanguageColor = (language: string) => {
    const colors: { [key: string]: string } = {
      JavaScript: '#f1e05a',
      TypeScript: '#3178c6',
      Python: '#3572A5',
      Java: '#b07219',
      'C++': '#f34b7d',
      C: '#555555',
      'C#': '#239120',
      PHP: '#4F5D95',
      Ruby: '#701516',
      Go: '#00ADD8',
      Swift: '#fa7343',
      Kotlin: '#A97BFF',
      Rust: '#dea584',
      Dart: '#00B4AB',
      HTML: '#e34c26',
      CSS: '#1572B6',
      Shell: '#89e051',
      Vue: '#41b883',
      React: '#61dafb',
    };
    return colors[language] || '#858585';
  };

  if (loading) {
    return (
      <div className="repository-detail">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading repository details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="repository-detail">
        <div className="error-container">
          <h2>Error</h2>
          <p>{error}</p>
          <div className="error-actions">
            <button onClick={() => navigate('/repositories')} className="btn-secondary">
              ← Back to Repositories
            </button>
            <button onClick={() => window.location.reload()} className="btn-primary">
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!repository) {
    return (
      <div className="repository-detail">
        <div className="error-container">
          <h2>Repository Not Found</h2>
          <p>The requested repository could not be found or you don't have access to it.</p>
          <button onClick={() => navigate('/repositories')} className="btn-secondary">
            ← Back to Repositories
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="repository-detail">
      {copyMessage && (
        <div className="copy-message">
          {copyMessage}
        </div>
      )}

      <div className="repo-header">
        <div className="repo-navigation">
          <Link to="/repositories" className="back-link">
            ← Back to Repositories
          </Link>
        </div>

        <div className="repo-title-section">
          <div className="repo-title">
            <div className="repo-title-main">
              <h1>{repository.name}</h1>
              <span className="repo-full-name">({repository.full_name})</span>
            </div>
            <div className="repo-badges">
              {repository.private && <span className="badge private">Private</span>}
              {repository.fork && <span className="badge fork">Fork</span>}
              {repository.archived && <span className="badge archived">Archived</span>}
              {repository.disabled && <span className="badge disabled">Disabled</span>}
            </div>
          </div>
          
          {repository.description && (
            <p className="repo-description">{repository.description}</p>
          )}

          {repository.topics && repository.topics.length > 0 && (
            <div className="repo-topics">
              {repository.topics.map((topic, index) => (
                <span key={index} className="topic-tag">{topic}</span>
              ))}
            </div>
          )}
        </div>

        <div className="repo-actions">
          <a 
            href={repository.html_url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="btn-primary"
          >
            <span>📂</span> View on GitHub
          </a>
          {repository.homepage && (
            <a 
              href={repository.homepage} 
              target="_blank" 
              rel="noopener noreferrer"
              className="btn-secondary"
            >
              <span>🌐</span> Visit Website
            </a>
          )}
        </div>
      </div>

      <div className="repo-content">
        <div className="repo-stats-grid">
          <div className="stat-card">
            <div className="stat-icon">⭐</div>
            <div className="stat-content">
              <div className="stat-value">{repository.stargazers_count.toLocaleString()}</div>
              <div className="stat-label">Stars</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">🍴</div>
            <div className="stat-content">
              <div className="stat-value">{repository.forks_count.toLocaleString()}</div>
              <div className="stat-label">Forks</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">👁️</div>
            <div className="stat-content">
              <div className="stat-value">{repository.watchers_count.toLocaleString()}</div>
              <div className="stat-label">Watchers</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">⚠️</div>
            <div className="stat-content">
              <div className="stat-value">{repository.open_issues_count.toLocaleString()}</div>
              <div className="stat-label">Open Issues</div>
            </div>
          </div>
        </div>

        <div className="repo-info-grid">
          <div className="info-section">
            <h3>Repository Information</h3>
            <div className="info-list">
              {repository.language && (
                <div className="info-item">
                  <span className="info-label">Primary Language:</span>
                  <div className="language-info">
                    <span 
                      className="language-color" 
                      style={{ backgroundColor: getLanguageColor(repository.language) }}
                    ></span>
                    <span className="language-name">{repository.language}</span>
                  </div>
                </div>
              )}
              
              <div className="info-item">
                <span className="info-label">Default Branch:</span>
                <span className="info-value">{repository.default_branch}</span>
              </div>
              
              <div className="info-item">
                <span className="info-label">Repository Size:</span>
                <span className="info-value">{formatFileSize(repository.size * 1024)}</span>
              </div>
              
              {repository.license && (
                <div className="info-item">
                  <span className="info-label">License:</span>
                  <span className="info-value">{repository.license.name}</span>
                </div>
              )}
              
              <div className="info-item">
                <span className="info-label">Visibility:</span>
                <span className="info-value">{repository.visibility}</span>
              </div>

              <div className="info-item">
                <span className="info-label">Owner:</span>
                <div className="owner-info">
                  <img 
                    src={repository.owner.avatar_url} 
                    alt={`${repository.owner.login} avatar`}
                    className="owner-avatar"
                  />
                  <a 
                    href={repository.owner.html_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="owner-link"
                  >
                    {repository.owner.login}
                  </a>
                </div>
              </div>
            </div>
          </div>

          <div className="info-section">
            <h3>Timeline</h3>
            <div className="info-list">
              <div className="info-item">
                <span className="info-label">Created:</span>
                <span className="info-value">{formatDate(repository.created_at)}</span>
              </div>
              
              <div className="info-item">
                <span className="info-label">Last Updated:</span>
                <span className="info-value">{formatDate(repository.updated_at)}</span>
              </div>
              
              {repository.pushed_at && (
                <div className="info-item">
                  <span className="info-label">Last Push:</span>
                  <span className="info-value">{formatDate(repository.pushed_at)}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="clone-section">
          <h3>Clone Repository</h3>
          <div className="clone-options">
            <div className="clone-option">
              <label>HTTPS:</label>
              <div className="clone-url-container">
                <input 
                  type="text" 
                  value={repository.clone_url} 
                  readOnly 
                  className="clone-url-input"
                />
                <button 
                  onClick={() => copyToClipboard(repository.clone_url, 'HTTPS URL')}
                  className="copy-btn"
                  title="Copy HTTPS URL"
                >
                  📋 Copy
                </button>
              </div>
            </div>

            <div className="clone-option">
              <label>SSH:</label>
              <div className="clone-url-container">
                <input 
                  type="text" 
                  value={repository.ssh_url} 
                  readOnly 
                  className="clone-url-input"
                />
                <button 
                  onClick={() => copyToClipboard(repository.ssh_url, 'SSH URL')}
                  className="copy-btn"
                  title="Copy SSH URL"
                >
                  📋 Copy
                </button>
              </div>
            </div>

            <div className="clone-option">
              <label>Git:</label>
              <div className="clone-url-container">
                <input 
                  type="text" 
                  value={repository.git_url} 
                  readOnly 
                  className="clone-url-input"
                />
                <button 
                  onClick={() => copyToClipboard(repository.git_url, 'Git URL')}
                  className="copy-btn"
                  title="Copy Git URL"
                >
                  📋 Copy
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RepositoryDetail;
