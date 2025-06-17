import React from 'react';
import { SortField, SortState } from './types';

interface RepositoryTableHeaderProps {
  currentSort: SortState;
  onSort: (field: SortField) => void;
}

const RepositoryTableHeader: React.FC<RepositoryTableHeaderProps> = ({
  currentSort,
  onSort,
}) => {
  const getSortIcon = (field: SortField) => {
    if (currentSort.field !== field) return '↕️';
    return currentSort.direction === 'asc' ? '↑' : '↓';
  };

  const getSortClass = (field: SortField) => {
    return currentSort.field === field ? 'active' : '';
  };

  return (
    <thead>
      <tr>
        <th className={currentSort.field === 'name' ? 'sorted' : ''}>
          <button
            className="sortable-header"
            onClick={() => onSort('name')}
            title="Sort by name"
          >
            Repository
            <span className={`sort-icon ${getSortClass('name')}`}>
              {getSortIcon('name')}
            </span>
          </button>
        </th>
        
        <th>Description</th>
        
        <th className={currentSort.field === 'language' ? 'sorted' : ''}>
          <button
            className="sortable-header"
            onClick={() => onSort('language')}
            title="Sort by language"
          >
            Language
            <span className={`sort-icon ${getSortClass('language')}`}>
              {getSortIcon('language')}
            </span>
          </button>
        </th>
        
        <th className={currentSort.field === 'stargazers_count' ? 'sorted' : ''}>
          <button
            className="sortable-header"
            onClick={() => onSort('stargazers_count')}
            title="Sort by stars"
          >
            Stars
            <span className={`sort-icon ${getSortClass('stargazers_count')}`}>
              {getSortIcon('stargazers_count')}
            </span>
          </button>
        </th>
        
        <th className={currentSort.field === 'forks_count' ? 'sorted' : ''}>
          <button
            className="sortable-header"
            onClick={() => onSort('forks_count')}
            title="Sort by forks"
          >
            Forks
            <span className={`sort-icon ${getSortClass('forks_count')}`}>
              {getSortIcon('forks_count')}
            </span>
          </button>
        </th>
        
        <th className={currentSort.field === 'size' ? 'sorted' : ''}>
          <button
            className="sortable-header"
            onClick={() => onSort('size')}
            title="Sort by size"
          >
            Size
            <span className={`sort-icon ${getSortClass('size')}`}>
              {getSortIcon('size')}
            </span>
          </button>
        </th>
        
        <th className={currentSort.field === 'updated_at' ? 'sorted' : ''}>
          <button
            className="sortable-header"
            onClick={() => onSort('updated_at')}
            title="Sort by last updated"
          >
            Updated
            <span className={`sort-icon ${getSortClass('updated_at')}`}>
              {getSortIcon('updated_at')}
            </span>
          </button>
        </th>
        
        <th>Actions</th>
      </tr>
    </thead>
  );
};

export default RepositoryTableHeader;
