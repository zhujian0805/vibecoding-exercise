import { PullRequest } from './types';

/**
 * Get badge class for pull request state
 */
export const getStateBadgeClass = (state: string, merged_at?: string): string => {
  if (merged_at) {
    return 'state-badge-merged';
  }
  switch (state) {
    case 'open':
      return 'state-badge-open';
    case 'closed':
      return 'state-badge-closed';
    default:
      return 'state-badge-unknown';
  }
};

/**
 * Get display text for pull request state
 */
export const getStateDisplayText = (state: string, merged_at?: string, draft?: boolean): string => {
  if (merged_at) {
    return 'Merged';
  }
  if (draft) {
    return 'Draft';
  }
  switch (state) {
    case 'open':
      return 'Open';
    case 'closed':
      return 'Closed';
    default:
      return state;
  }
};

/**
 * Format date to relative time
 */
export const formatDate = (dateString: string): string => {
  if (!dateString) return 'Unknown';
  
  const date = new Date(dateString);
  const now = new Date();
  const diffInMs = now.getTime() - date.getTime();
  const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));
  
  if (diffInDays === 0) {
    const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
    if (diffInHours === 0) {
      const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
      return diffInMinutes <= 1 ? 'just now' : `${diffInMinutes} minutes ago`;
    }
    return diffInHours === 1 ? '1 hour ago' : `${diffInHours} hours ago`;
  } else if (diffInDays === 1) {
    return 'yesterday';
  } else if (diffInDays < 30) {
    return `${diffInDays} days ago`;
  } else if (diffInDays < 365) {
    const diffInMonths = Math.floor(diffInDays / 30);
    return diffInMonths === 1 ? '1 month ago' : `${diffInMonths} months ago`;
  } else {
    const diffInYears = Math.floor(diffInDays / 365);
    return diffInYears === 1 ? '1 year ago' : `${diffInYears} years ago`;
  }
};

/**
 * Format number with appropriate suffix (K, M)
 */
export const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1).replace(/\.0$/, '') + 'M';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'K';
  }
  return num.toString();
};

/**
 * Copy text to clipboard
 */
export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return true;
    } else {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      textArea.style.top = '-999999px';
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      const result = document.execCommand('copy');
      textArea.remove();
      return result;
    }
  } catch (err) {
    console.error('Failed to copy text: ', err);
    return false;
  }
};

/**
 * Get branch display name
 */
export const getBranchDisplayName = (branch?: { ref: string; label?: string }): string => {
  if (!branch) return 'unknown';
  return branch.label || branch.ref || 'unknown';
};

/**
 * Get changes summary text
 */
export const getChangesSummary = (additions: number, deletions: number): string => {
  if (additions === 0 && deletions === 0) {
    return 'No changes';
  }
  
  const parts: string[] = [];
  if (additions > 0) {
    parts.push(`+${formatNumber(additions)}`);
  }
  if (deletions > 0) {
    parts.push(`-${formatNumber(deletions)}`);
  }
  
  return parts.join(' ');
};

/**
 * Truncate text to specified length
 */
export const truncateText = (text: string, maxLength: number): string => {
  if (!text || text.length <= maxLength) {
    return text || '';
  }
  return text.substring(0, maxLength) + '...';
};

/**
 * Get sort icon class based on current sort state
 */
export const getSortIcon = (field: string, currentSort: { field: string | null; direction: 'asc' | 'desc' }): string => {
  if (currentSort.field !== field) {
    return 'sort-icon';
  }
  return currentSort.direction === 'asc' ? 'sort-icon sort-icon-asc' : 'sort-icon sort-icon-desc';
};

/**
 * Filter pull requests based on search query
 */
export const filterPullRequests = (prs: PullRequest[], query: string): PullRequest[] => {
  if (!query.trim()) {
    return prs;
  }
  
  const searchTerm = query.toLowerCase().trim();
  
  return prs.filter(pr => {
    return (
      pr.title.toLowerCase().includes(searchTerm) ||
      (pr.body && pr.body.toLowerCase().includes(searchTerm)) ||
      (pr.user && pr.user.login.toLowerCase().includes(searchTerm)) ||
      (pr.repository && pr.repository.name.toLowerCase().includes(searchTerm)) ||
      (pr.repository && pr.repository.full_name.toLowerCase().includes(searchTerm)) ||
      pr.number.toString().includes(searchTerm)
    );
  });
};
