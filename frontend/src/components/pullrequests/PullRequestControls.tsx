import React from 'react';

interface PullRequestControlsProps {
  sortBy: string;
  onSortChange: (sort: string) => void;
  loading: boolean;
  totalCount: number;
  searchQuery: string;
}

const PullRequestControls: React.FC<PullRequestControlsProps> = ({
  sortBy,
  onSortChange,
  loading,
  totalCount,
  searchQuery
}) => {
  return (
    <div className="pullrequests-controls">
      <div className="controls-section">
        <div className="controls-group">
          <label htmlFor="sort-select" className="control-label">
            Sort by:
          </label>
          <select
            id="sort-select"
            value={sortBy}
            onChange={(e) => onSortChange(e.target.value)}
            className="sort-select"
            disabled={loading}
          >
            <option value="updated">Recently Updated</option>
            <option value="created">Recently Created</option>
            <option value="comments">Most Commented</option>
            <option value="commits">Most Commits</option>
          </select>
        </div>
      </div>
      
      <div className="results-info">
        {searchQuery ? (
          <span>
            {totalCount} result{totalCount !== 1 ? 's' : ''} for "{searchQuery}"
          </span>
        ) : (
          <span>
            {totalCount} pull request{totalCount !== 1 ? 's' : ''} total
          </span>
        )}
      </div>
    </div>
  );
};

export default PullRequestControls;
