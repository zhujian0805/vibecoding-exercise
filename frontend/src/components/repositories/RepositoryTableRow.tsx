import React from 'react';
import { Repository } from './types';

interface RepositoryTableRowProps {
  repository: Repository;
  onCopyCloneUrl: (cloneUrl: string, repoName: string) => void;
  getLanguageColor: (language: string) => string;
  formatDate: (dateString: string) => string;
}

const RepositoryTableRow: React.FC<RepositoryTableRowProps> = ({
  repository: repo,
  onCopyCloneUrl,
  getLanguageColor,
  formatDate,
}) => {
  return (
    <tr>
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
              {repo.topics.slice(0, 3).map((topic, index) => (
                <span key={index} className="topic-tag">{topic}</span>
              ))}
              {repo.topics.length > 3 && (
                <span className="topic-tag more">+{repo.topics.length - 3}</span>
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
        <span className="stat-value">{repo.stargazers_count}</span>
      </td>
      
      <td className="forks-cell">
        <span className="stat-value">{repo.forks_count}</span>
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
            onClick={() => onCopyCloneUrl(repo.clone_url, repo.name)}
            className="action-btn clone-btn"
            title="Copy clone URL"
          >
            Copy
          </button>
        </div>
      </td>
    </tr>
  );
};

export default RepositoryTableRow;
