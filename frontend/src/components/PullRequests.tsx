import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import PullRequestTableHeader from './pullrequests/PullRequestTableHeader';
import PullRequestTableRow from './pullrequests/PullRequestTableRow';
import {
  PullRequest,
  PullRequestsResponse,
  SortField,
  SortDirection,
} from './pullrequests/types';

const API_BASE_URL = 'http://localhost:5000';

const PullRequests: React.FC = () => {
  const [pullRequests, setPullRequests] = useState<PullRequest[]>([]);
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

  const fetchPullRequests = useCallback(async () => {
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
      
      // Include search query if provided
      if (searchQuery) {
        params.append('q', searchQuery);
      }

      const response = await axios.get<PullRequestsResponse>(
        `${API_BASE_URL}/api/pullrequests?${params}`,
        { withCredentials: true }
      );
      
      setPullRequests(response.data.pullrequests || []);
      setPage(response.data.page || 1);
      setPerPage(response.data.per_page || 30);
      setTotalPages(response.data.total_pages || 1);
      setTotalCount(response.data.total_count || 0);
      setHasNext(response.data.has_next || false);
      setHasPrev(response.data.has_prev || false);
      
    } catch (error: any) {
      console.error('Error fetching pull requests:', error);
      if (error.response?.status === 401) {
        setError('Authentication required. Please log in again.');
      } else if (error.response?.status === 403) {
        setError('GitHub API rate limit exceeded. Please try again later.');
      } else {
        setError('Failed to load pull requests. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  }, [page, perPage, sortBy, currentSort, searchQuery]);

  useEffect(() => {
    fetchPullRequests();
  }, [fetchPullRequests]);

  const handleSearch = () => {
    setSearchQuery(searchInput);
    setPage(1); // Reset to first page when searching
  };

  const handleClearSearch = () => {
    setSearchQuery('');
    setSearchInput('');
    setPage(1);
  };

  const handleSort = (field: SortField) => {
    const newDirection = currentSort.field === field && currentSort.direction === 'asc' ? 'desc' : 'asc';
    setCurrentSort({ field, direction: newDirection });
    setPage(1); // Reset to first page when sorting
  };

  const handlePerPageChange = (newPerPage: number) => {
    setPerPage(newPerPage);
    setPage(1); // Reset to first page when changing page size
  };

  const retry = () => {
    fetchPullRequests();
  };

  if (loading && pullRequests.length === 0) {
    return (
      <div className="pullrequests">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading pull requests...</p>
        </div>
      </div>
    );
  }

  if (error && pullRequests.length === 0) {
    return (
      <div className="pullrequests">
        <div className="error">
          <h2>Error Loading Pull Requests</h2>
          <p>{error}</p>
          <button onClick={retry} className="retry-button">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="pullrequests">
      {copyMessage && (
        <div className="copy-message">
          {copyMessage}
        </div>
      )}
      
      <div className="pullrequests-header">
        <div className="pullrequests-title-row">
          <h1>Pull Requests</h1>
        </div>
        
        {/* Compact Controls Section - All in one frame */}
        <div className="pullrequests-compact-controls">
          <form onSubmit={(e) => { e.preventDefault(); handleSearch(); }} className="search-form">
            <div className="search-input-container">
              <input
                type="text"
                placeholder="Search pull requests by title, body, author, repository, or number..."
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
                <option value="comments">Most Commented</option>
                <option value="commits">Most Commits</option>
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

      {pullRequests.length === 0 ? (
        <div className="no-pullrequests">
          <p>No pull requests found.</p>
        </div>
      ) : (
        <>
          {/* Pagination controls above the table */}
          <div className="pagination">
            <div className="pagination-info">
              Showing {((page - 1) * perPage) + 1} to {Math.min(page * perPage, totalCount)} of {totalCount} pull requests
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

          <div className="pullrequests-table-container">
            <table className="pullrequests-table">
              <PullRequestTableHeader
                currentSort={currentSort}
                onSort={handleSort}
              />
              <tbody>
                {pullRequests.map((pr) => (
                  <PullRequestTableRow
                    key={pr.id}
                    pr={pr}
                    onCopy={(message) => {
                      setCopyMessage(message);
                      setTimeout(() => setCopyMessage(null), 2000);
                    }}
                  />
                ))}
              </tbody>
            </table>
          </div>

          <div className="pagination">
            <div className="pagination-info">
              Showing {((page - 1) * perPage) + 1} to {Math.min(page * perPage, totalCount)} of {totalCount} pull requests
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
                onClick={() => setPage(p => p + 1)}
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
        </>
      )}

      {pullRequests.length === 0 && !loading && (
        <div className="empty-state">
          <div className="empty-icon">📋</div>
          <h3>No Pull Requests Found</h3>
          <p>
            {searchQuery 
              ? 'Try adjusting your search terms or filters.'
              : 'You don\'t have any pull requests yet.'
            }
          </p>
          {searchQuery && (
            <button onClick={handleClearSearch} className="clear-search-button">
              Clear Search
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default PullRequests;
