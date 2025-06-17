import React from 'react';

interface RepositorySearchProps {
  searchInput: string;
  searchQuery: string;
  onSearchInputChange: (value: string) => void;
  onSearch: (e: React.FormEvent) => void;
  onClearSearch: () => void;
}

const RepositorySearch: React.FC<RepositorySearchProps> = ({
  searchInput,
  searchQuery,
  onSearchInputChange,
  onSearch,
  onClearSearch,
}) => {
  return (
    <form onSubmit={onSearch} className="search-form">
      <div className="search-input-container">
        <input
          type="text"
          placeholder="Search repositories..."
          value={searchInput}
          onChange={(e) => onSearchInputChange(e.target.value)}
          className="search-input"
        />
        {searchInput && (
          <button
            type="button"
            onClick={onClearSearch}
            className="clear-search-btn"
            title="Clear search"
          >
            ×
          </button>
        )}
      </div>
      <button type="submit" className="search-btn">
        Search
      </button>
      {searchQuery && (
        <div className="search-info">
          <strong>Searching for:</strong> "{searchQuery}"
        </div>
      )}
    </form>
  );
};

export default RepositorySearch;
