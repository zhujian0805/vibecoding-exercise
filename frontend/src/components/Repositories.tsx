import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import RepositorySearch from './repositories/RepositorySearch';
import RepositoryControls from './repositories/RepositoryControls';
import RepositoryTableHeader from './repositories/RepositoryTableHeader';
import RepositoryTableRow from './repositories/RepositoryTableRow';
import RepositoryPagination from './repositories/RepositoryPagination';
import { getLanguageColor, formatDate, copyToClipboard } from './repositories/utils';
import {
  Repository,
  RepositoriesResponse,
  SortField,
  SortDirection,
  SortState,
  PaginationState,
} from './repositories/types';

const API_BASE_URL = 'http://localhost:5000';

const Repositories: React.FC = () => {
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(30);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [hasNext, setHasNext] = useState(false);
  const [hasPrev, setHasPrev] = useState(false);
  const [sortBy, setSortBy] = useState('updated');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchInput, setSearchInput] = useState('');
  const [copyMessage, setCopyMessage] = useState<string | null>(null);
  const [currentSort, setCurrentSort] = useState<{ field: SortField | null; direction: SortDirection }>({
    field: null,
    direction: 'asc'
  });

  const fetchRepositories = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const params = new URLSearchParams({
        page: page.toString(),
        per_page: perPage.toString(),
        sort: sortBy
      });
      
      // Include table sorting parameters if they exist
      if (currentSort.field) {
        params.append('table_sort', currentSort.field);
        params.append('table_sort_direction', currentSort.direction);
      }
      
      if (searchQuery.trim()) {
        params.append('search', searchQuery.trim());
      }
      
      console.log(`[DEBUG] Fetching repositories - Page: ${page}, Per Page: ${perPage}, Sort: ${sortBy}, Table Sort: ${currentSort.field}:${currentSort.direction}`);
      
      const response = await axios.get<RepositoriesResponse>(
        `${API_BASE_URL}/api/repositories?${params.toString()}`,
        { withCredentials: true }
      );
      
      console.log(`[DEBUG] Response received - Total: ${response.data.total_count}, Current page: ${response.data.page}, Has next: ${response.data.has_next}`);
      
      setRepositories(response.data.repositories);
      setTotalPages(response.data.total_pages);
      setTotalCount(response.data.total_count);
      setHasNext(response.data.has_next);
      setHasPrev(response.data.has_prev);
      // Don't reset client-side sorting when fetching with existing sort parameters
      if (!currentSort.field) {
        setCurrentSort({ field: null, direction: 'asc' });
      }
    } catch (err) {
      setError('Failed to fetch repositories');
      console.error('Error fetching repositories:', err);
    } finally {
      setLoading(false);
    }
  }, [page, perPage, sortBy, searchQuery, currentSort.field, currentSort.direction]);

  useEffect(() => {
    fetchRepositories();
  }, [fetchRepositories]);

  // Reset to page 1 when search query changes
  useEffect(() => {
    setPage(1);
  }, [searchQuery]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setSearchQuery(searchInput);
  };

  const handleClearSearch = () => {
    setSearchInput('');
    setSearchQuery('');
  };

  const handlePerPageChange = (newPerPage: number) => {
    setPerPage(newPerPage);
    setPage(1); // Reset to first page when changing items per page
  };

  const handleCopyCloneUrl = async (cloneUrl: string, repoName: string) => {
    try {
      await navigator.clipboard.writeText(cloneUrl);
      setCopyMessage(`Clone URL copied for ${repoName}!`);
      setTimeout(() => setCopyMessage(null), 3000);
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
      setCopyMessage('Failed to copy clone URL');
      setTimeout(() => setCopyMessage(null), 3000);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getLanguageColor = (language: string) => {
    const colors: { [key: string]: string } = {
      JavaScript: '#f1e05a',
      TypeScript: '#2b7489',
      Python: '#3572A5',
      Java: '#b07219',
      'C++': '#f34b7d',
      C: '#555555',
      'C#': '#239120',
      PHP: '#4F5D95',
      Go: '#00ADD8',
      Rust: '#dea584',
      Swift: '#ffac45',
      Kotlin: '#F18E33',
      Ruby: '#701516',
      HTML: '#e34c26',
      CSS: '#1572B6',
      Shell: '#89e051',
    };
    return colors[language] || '#586069';
  };

  // Handle table column sorting - now sends request to backend
  const handleSort = async (field: SortField) => {
    let direction: SortDirection = 'asc';
    
    // Toggle direction if clicking the same field
    if (currentSort.field === field && currentSort.direction === 'asc') {
      direction = 'desc';
    }

    try {
      setLoading(true);
      setError(null);
      
      const params = new URLSearchParams({
        page: page.toString(),
        per_page: perPage.toString(),
        sort: sortBy,
        table_sort: field,
        table_sort_direction: direction
      });
      
      if (searchQuery.trim()) {
        params.append('search', searchQuery.trim());
      }
      
      console.log(`[DEBUG] Sorting repositories - Field: ${field}, Direction: ${direction}`);
      
      const response = await axios.get<RepositoriesResponse>(
        `${API_BASE_URL}/api/repositories?${params.toString()}`,
        { withCredentials: true }
      );
      
      console.log(`[DEBUG] Sort response received - Total: ${response.data.total_count}, Current page: ${response.data.page}`);
      
      setRepositories(response.data.repositories);
      setTotalPages(response.data.total_pages);
      setTotalCount(response.data.total_count);
      setHasNext(response.data.has_next);
      setHasPrev(response.data.has_prev);
      setCurrentSort({ field, direction });
    } catch (err) {
      setError('Failed to sort repositories');
      console.error('Error sorting repositories:', err);
    } finally {
      setLoading(false);
    }
  };

  // Get sort icon for table headers
  const getSortIcon = (field: SortField) => {
    if (currentSort.field !== field) {
      return <span className="sort-icon">↕</span>;
    }
    return currentSort.direction === 'asc' ? 
      <span className="sort-icon active">↑</span> : 
      <span className="sort-icon active">↓</span>;
  };

  if (loading) {
    return (
      <div className="repositories">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading repositories...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="repositories">
        <div className="error-message">
          {error}
          <button onClick={fetchRepositories} className="retry-btn">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="repositories">
      {copyMessage && (
        <div className="copy-message">
          {copyMessage}
        </div>
      )}
      
      <div className="repositories-header">
        <div className="repositories-title-row">
          <h1>My Repositories</h1>
        </div>
        
        {/* Compact Controls Section - All in one frame */}
        <div className="repositories-compact-controls">
          <form onSubmit={handleSearch} className="search-form">
            <div className="search-input-container">
              <input
                type="text"
                placeholder="Search repositories by name or description..."
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                className="search-input"
              />
              {searchInput && (
                <button
                  type="button"
                  onClick={handleClearSearch}
                  className="clear-search-btn"
                  title="Clear search"
                >
                  ✕
                </button>
              )}
            </div>
            <button type="submit" className="search-btn">
              Search
            </button>
          </form>
          
          <div className="control-group">
            <label>
              Sort by:
              <select 
                value={sortBy} 
                onChange={(e) => {
                  setSortBy(e.target.value);
                  // Reset table sorting when main sort changes
                  setCurrentSort({ field: null, direction: 'asc' });
                }}
                className="sort-select"
              >
                <option value="updated">Recently Updated</option>
                <option value="created">Recently Created</option>
                <option value="pushed">Recently Pushed</option>
                <option value="full_name">Name</option>
              </select>
            </label>
          </div>
          
          <div className="control-group">
            <label>
              Items per page:
              <select 
                value={perPage} 
                onChange={(e) => handlePerPageChange(Number(e.target.value))}
                className="per-page-select"
              >
                <option value={10}>10</option>
                <option value={20}>20</option>
                <option value={30}>30</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
            </label>
          </div>
        </div>
        
        {/* Search Results Info */}
        {searchQuery && (
          <div className="search-info">
            Searching for: "<strong>{searchQuery}</strong>" 
            ({totalCount} result{totalCount !== 1 ? 's' : ''})
          </div>
        )}
      </div>

      {repositories.length === 0 ? (
        <div className="no-repositories">
          <p>No repositories found.</p>
        </div>
      ) : (
        <>
          {/* Pagination controls above the table */}
          <div className="pagination">
            <div className="pagination-info">
              Showing {((page - 1) * perPage) + 1} to {Math.min(page * perPage, totalCount)} of {totalCount} repositories
              {totalPages > 1 && ` (Page ${page} of ${totalPages})`}
            </div>
            
            <div className="pagination-controls">
              <button 
                onClick={() => setPage(1)}
                disabled={!hasPrev}
                className="page-btn first-btn"
              >
                First
              </button>
              <button 
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={!hasPrev}
                className="page-btn"
              >
                Previous
              </button>
              
              <div className="page-numbers">
                {/* Show page numbers around current page */}
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  let pageNum: number;
                  if (totalPages <= 5) {
                    pageNum = i + 1;
                  } else if (page <= 3) {
                    pageNum = i + 1;
                  } else if (page >= totalPages - 2) {
                    pageNum = totalPages - 4 + i;
                  } else {
                    pageNum = page - 2 + i;
                  }
                  
                  return (
                    <button
                      key={pageNum}
                      onClick={() => setPage(pageNum)}
                      className={`page-btn ${page === pageNum ? 'active' : ''}`}
                    >
                      {pageNum}
                    </button>
                  );
                })}
              </div>
              
              <button 
                onClick={() => {
                  console.log(`[DEBUG] Next button clicked - Current page: ${page}, Going to: ${page + 1}`);
                  setPage(p => p + 1);
                }}
                disabled={!hasNext}
                className="page-btn"
              >
                Next
              </button>
              <button 
                onClick={() => setPage(totalPages)}
                disabled={!hasNext}
                className="page-btn last-btn"
              >
                Last
              </button>
            </div>
          </div>

          <div className="repositories-table-container">
            <table className="repositories-table">
            <thead>
              <tr>
                <th className={`repo-name-cell ${currentSort.field === 'name' ? 'sorted' : ''}`}>
                  <div 
                    className="sortable-header" 
                    onClick={() => handleSort('name')}
                    onKeyDown={(e) => e.key === 'Enter' && handleSort('name')}
                    title="Click to sort by repository name"
                    tabIndex={0}
                    role="button"
                  >
                    <span>Repository</span>
                    {getSortIcon('name')}
                  </div>
                </th>
                <th className="repo-description-cell">
                  <span>Description</span>
                </th>
                <th className={`language-cell ${currentSort.field === 'language' ? 'sorted' : ''}`}>
                  <div 
                    className="sortable-header" 
                    onClick={() => handleSort('language')}
                    onKeyDown={(e) => e.key === 'Enter' && handleSort('language')}
                    title="Click to sort by language"
                    tabIndex={0}
                    role="button"
                  >
                    <span>Lang</span>
                    {getSortIcon('language')}
                  </div>
                </th>
                <th className={`stars-cell ${currentSort.field === 'stargazers_count' ? 'sorted' : ''}`}>
                  <div 
                    className="sortable-header" 
                    onClick={() => handleSort('stargazers_count')}
                    onKeyDown={(e) => e.key === 'Enter' && handleSort('stargazers_count')}
                    title="Click to sort by stars"
                    tabIndex={0}
                    role="button"
                  >
                    <span>⭐</span>
                    {getSortIcon('stargazers_count')}
                  </div>
                </th>
                <th className={`forks-cell ${currentSort.field === 'forks_count' ? 'sorted' : ''}`}>
                  <div 
                    className="sortable-header" 
                    onClick={() => handleSort('forks_count')}
                    onKeyDown={(e) => e.key === 'Enter' && handleSort('forks_count')}
                    title="Click to sort by forks"
                    tabIndex={0}
                    role="button"
                  >
                    <span>🍴</span>
                    {getSortIcon('forks_count')}
                  </div>
                </th>
                <th className={`size-cell ${currentSort.field === 'size' ? 'sorted' : ''}`}>
                  <div 
                    className="sortable-header" 
                    onClick={() => handleSort('size')}
                    onKeyDown={(e) => e.key === 'Enter' && handleSort('size')}
                    title="Click to sort by size"
                    tabIndex={0}
                    role="button"
                  >
                    <span>Size</span>
                    {getSortIcon('size')}
                  </div>
                </th>
                <th className={`updated-cell ${currentSort.field === 'updated_at' ? 'sorted' : ''}`}>
                  <div 
                    className="sortable-header" 
                    onClick={() => handleSort('updated_at')}
                    onKeyDown={(e) => e.key === 'Enter' && handleSort('updated_at')}
                    title="Click to sort by last updated"
                    tabIndex={0}
                    role="button"
                  >
                    <span>Updated</span>
                    {getSortIcon('updated_at')}
                  </div>
                </th>
                <th className="actions-cell">
                  <span>Actions</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {repositories.map((repo) => (
                <RepositoryTableRow
                  key={repo.id}
                  repository={repo}
                  onCopyCloneUrl={handleCopyCloneUrl}
                  getLanguageColor={getLanguageColor}
                  formatDate={formatDate}
                />
              ))}
            </tbody>
          </table>
          </div>
        </>
      )}
    </div>
  );
};

export default Repositories;
