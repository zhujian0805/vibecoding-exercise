import React from 'react';
import { PullRequest } from './types';
import { 
  getStateBadgeClass, 
  getStateDisplayText, 
  formatDate, 
  formatNumber, 
  copyToClipboard,
  getBranchDisplayName,
  getChangesSummary,
  truncateText
} from './utils';

interface PullRequestTableRowProps {
  pr: PullRequest;
  onCopy: (message: string) => void;
}

const PullRequestTableRow: React.FC<PullRequestTableRowProps> = ({ pr, onCopy }) => {
  const handleCopyUrl = async () => {
    if (pr.html_url) {
      const success = await copyToClipboard(pr.html_url);
      if (success) {
        onCopy(`Copied PR #${pr.number} URL to clipboard`);
      }
    }
  };

  const handleCopyBranch = async () => {
    const branchInfo = `${getBranchDisplayName(pr.base)} ← ${getBranchDisplayName(pr.head)}`;
    const success = await copyToClipboard(branchInfo);
    if (success) {
      onCopy('Copied branch info to clipboard');
    }
  };

  const stateClass = getStateBadgeClass(pr.state, pr.merged_at);
  const stateText = getStateDisplayText(pr.state, pr.merged_at, pr.draft);

  return (
    <tr className="pr-row">
      <td className="pr-number">
        <a 
          href={pr.html_url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="pr-number-link"
          title={`View PR #${pr.number} on GitHub`}
        >
          #{pr.number}
        </a>
      </td>
      
      <td className="pr-title">
        <div className="pr-title-container">
          <a 
            href={pr.html_url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="pr-title-link"
            title={pr.title}
          >
            {truncateText(pr.title, 60)}
          </a>
          {pr.draft && <span className="draft-badge">Draft</span>}
        </div>
        {pr.body && (
          <div className="pr-description" title={pr.body}>
            {truncateText(pr.body, 80)}
          </div>
        )}
        <div className="branch-info" title="Click to copy branch info">
          <button 
            onClick={handleCopyBranch}
            className="branch-button"
          >
            {getBranchDisplayName(pr.base)} ← {getBranchDisplayName(pr.head)}
          </button>
        </div>
      </td>
      
      <td className="pr-state">
        <span className={`state-badge ${stateClass}`}>
          {stateText}
        </span>
      </td>
      
      <td className="pr-author">
        {pr.user && (
          <div className="author-info">
            <img 
              src={pr.user.avatar_url} 
              alt={pr.user.login} 
              className="author-avatar"
            />
            <a 
              href={pr.user.html_url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="author-link"
            >
              {pr.user.login}
            </a>
          </div>
        )}
      </td>
      
      <td className="pr-repository">
        {pr.repository && (
          <a 
            href={pr.repository.html_url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="repo-link"
            title={pr.repository.full_name}
          >
            {pr.repository.name}
          </a>
        )}
      </td>
      
      <td className="pr-comments">
        <div className="comments-info">
          {pr.comments > 0 && (
            <span className="comments-count" title={`${pr.comments} comments`}>
              💬 {formatNumber(pr.comments)}
            </span>
          )}
          {pr.review_comments > 0 && (
            <span className="review-comments-count" title={`${pr.review_comments} review comments`}>
              🔍 {formatNumber(pr.review_comments)}
            </span>
          )}
          {pr.comments === 0 && pr.review_comments === 0 && (
            <span className="no-comments">—</span>
          )}
        </div>
      </td>
      
      <td className="pr-changes">
        <div className="changes-info">
          {(pr.additions > 0 || pr.deletions > 0) ? (
            <div className="changes-summary" title={`${pr.additions} additions, ${pr.deletions} deletions, ${pr.changed_files} files changed`}>
              <span className="changes-text">{getChangesSummary(pr.additions, pr.deletions)}</span>
              <span className="files-changed">{pr.changed_files} file{pr.changed_files !== 1 ? 's' : ''}</span>
            </div>
          ) : (
            <span className="no-changes">—</span>
          )}
        </div>
      </td>
      
      <td className="pr-updated">
        <span title={pr.updated_at}>
          {formatDate(pr.updated_at || '')}
        </span>
      </td>
      
      <td className="pr-actions">
        <div className="actions-group">
          {pr.html_url && (
            <button
              onClick={handleCopyUrl}
              className="action-btn copy-btn"
              title="Copy PR URL"
            >
              📋
            </button>
          )}
          {pr.html_url && (
            <a
              href={pr.html_url}
              target="_blank"
              rel="noopener noreferrer"
              className="action-btn external-btn"
              title="Open in GitHub"
            >
              🔗
            </a>
          )}
        </div>
      </td>
    </tr>
  );
};

export default PullRequestTableRow;
