import React from 'react';

interface PullRequestSearchProps {
  searchInput: string;
  onSearchInputChange: (value: string) => void;
  onSearch: () => void;
  onClear: () => void;
  loading: boolean;
}

const PullRequestSearch: React.FC<PullRequestSearchProps> = ({
  searchInput,
  onSearchInputChange,
  onSearch,
  onClear,
  loading
}) => {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      onSearch();
    }
  };

  return (
    <div className="search-section">
      <form onSubmit={handleSubmit} className="search-form">
        <div className="search-input-container">
          <input
            type="text"
            value={searchInput}
            onChange={(e) => onSearchInputChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search pull requests by title, body, author, repository, or number..."
            className="search-input"
            disabled={loading}
          />
          {searchInput && (
            <button
              type="button"
              onClick={onClear}
              className="search-clear-btn"
              title="Clear search"
              disabled={loading}
            >
              ×
            </button>
          )}
        </div>
        <button
          type="submit"
          className="search-btn"
          disabled={loading}
        >
          Search
        </button>
      </form>
    </div>
  );
};

export default PullRequestSearch;
