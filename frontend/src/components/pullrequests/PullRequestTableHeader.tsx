import React from 'react';
import { SortField, SortDirection } from './types';

interface PullRequestTableHeaderProps {
  currentSort: {
    field: SortField | null;
    direction: SortDirection;
  };
  onSort: (field: SortField) => void;
}

const PullRequestTableHeader: React.FC<PullRequestTableHeaderProps> = ({
  currentSort,
  onSort
}) => {
  const getSortIcon = (field: SortField) => {
    if (currentSort.field !== field) {
      return '↕️'; // Both directions available
    }
    return currentSort.direction === 'asc' ? '↑' : '↓';
  };

  const getSortClass = (field: SortField) => {
    const baseClass = 'sortable-header';
    if (currentSort.field === field) {
      return `${baseClass} active`;
    }
    return baseClass;
  };

  return (
    <thead>
      <tr className="pr-header-row">
        <th className="pr-number-header">
          <button 
            className={getSortClass('number')}
            onClick={() => onSort('number')}
            title="Sort by PR number"
          >
            # {getSortIcon('number')}
          </button>
        </th>
        
        <th className="pr-title-header">
          <button 
            className={getSortClass('title')}
            onClick={() => onSort('title')}
            title="Sort by title"
          >
            Title {getSortIcon('title')}
          </button>
        </th>
        
        <th className="pr-state-header">
          <button 
            className={getSortClass('state')}
            onClick={() => onSort('state')}
            title="Sort by state"
          >
            State {getSortIcon('state')}
          </button>
        </th>
        
        <th className="pr-author-header">
          <button 
            className={getSortClass('author')}
            onClick={() => onSort('author')}
            title="Sort by author"
          >
            Author {getSortIcon('author')}
          </button>
        </th>
        
        <th className="pr-repository-header">
          <button 
            className={getSortClass('repository')}
            onClick={() => onSort('repository')}
            title="Sort by repository"
          >
            Repository {getSortIcon('repository')}
          </button>
        </th>
        
        <th className="pr-comments-header">
          <button 
            className={getSortClass('comments')}
            onClick={() => onSort('comments')}
            title="Sort by comments"
          >
            Comments {getSortIcon('comments')}
          </button>
        </th>
        
        <th className="pr-changes-header">
          <button 
            className={getSortClass('additions')}
            onClick={() => onSort('additions')}
            title="Sort by changes"
          >
            Changes {getSortIcon('additions')}
          </button>
        </th>
        
        <th className="pr-updated-header">
          <button 
            className={getSortClass('updated_at')}
            onClick={() => onSort('updated_at')}
            title="Sort by last updated"
          >
            Updated {getSortIcon('updated_at')}
          </button>
        </th>
        
        <th className="pr-actions-header">
          <span>Actions</span>
        </th>
      </tr>
    </thead>
  );
};

export default PullRequestTableHeader;
