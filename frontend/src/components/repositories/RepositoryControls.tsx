import React from 'react';

interface RepositoryControlsProps {
  sortBy: string;
  perPage: number;
  onSortChange: (value: string) => void;
  onPerPageChange: (value: number) => void;
}

const RepositoryControls: React.FC<RepositoryControlsProps> = ({
  sortBy,
  perPage,
  onSortChange,
  onPerPageChange,
}) => {
  return (
    <div className="repositories-compact-controls">
      <div className="control-group">
        <label>
          Sort by:
          <select 
            value={sortBy} 
            onChange={(e) => onSortChange(e.target.value)}
            className="sort-select"
          >
            <option value="updated">Recently Updated</option>
            <option value="name">Name</option>
            <option value="stars">Stars</option>
            <option value="forks">Forks</option>
            <option value="size">Size</option>
          </select>
        </label>
      </div>
      
      <div className="control-group">
        <label>
          Per page:
          <select 
            value={perPage} 
            onChange={(e) => onPerPageChange(Number(e.target.value))}
            className="per-page-select"
          >
            <option value={10}>10</option>
            <option value={30}>30</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
          </select>
        </label>
      </div>
    </div>
  );
};

export default RepositoryControls;
