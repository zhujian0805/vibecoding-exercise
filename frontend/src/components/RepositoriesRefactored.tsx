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
  SortState,
  PaginationState,
} from './repositories/types';

const API_BASE_URL = 'http://localhost:5000';

const RepositoriesRefactored: React.FC = () => {
  // State management
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Pagination state
  const [pagination, setPagination] = useState<PaginationState>({
    page: 1,
    perPage: 30,
    totalPages: 1,
    totalCount: 0,
    hasNext: false,
    hasPrev: false,
  });
  
  // Search and sorting state
  const [sortBy, setSortBy] = useState('updated');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchInput, setSearchInput] = useState('');
  const [copyMessage, setCopyMessage] = useState<string | null>(null);
  const [currentSort, setCurrentSort] = useState<SortState>({
    field: null,
    direction: 'asc',
  });

  // Data fetching
  const fetchRepositories = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams({
        page: pagination.page.toString(),
        per_page: pagination.perPage.toString(),
        sort: sortBy,
      });

      if (searchQuery) {
        params.append('search', searchQuery);
      }

      if (currentSort.field) {
        params.append('table_sort', currentSort.field);
        params.append('table_sort_direction', currentSort.direction);
      }

      const response = await axios.get<RepositoriesResponse>(
        `${API_BASE_URL}/repositories?${params}`,
        { withCredentials: true }
      );

      const data = response.data;
      setRepositories(data.repositories);
      setPagination({
        page: data.page,
        perPage: data.per_page,
        totalPages: data.total_pages,
        totalCount: data.total_count,
        hasNext: data.has_next,
        hasPrev: data.has_prev,
      });
    } catch (err) {
      console.error('Error fetching repositories:', err);
      setError('Failed to fetch repositories. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [pagination.page, pagination.perPage, sortBy, searchQuery, currentSort]);

  // Effects
  useEffect(() => {
    fetchRepositories();
  }, [fetchRepositories]);

  // Event handlers
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setSearchQuery(searchInput);
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handleClearSearch = () => {
    setSearchInput('');
    setSearchQuery('');
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handlePerPageChange = (newPerPage: number) => {
    setPagination(prev => ({
      ...prev,
      perPage: newPerPage,
      page: 1,
    }));
  };

  const handlePageChange = (newPage: number) => {
    setPagination(prev => ({ ...prev, page: newPage }));
  };

  const handleCopyCloneUrl = async (cloneUrl: string, repoName: string) => {
    const success = await copyToClipboard(cloneUrl);
    if (success) {
      setCopyMessage(`Copied clone URL for ${repoName}`);
      setTimeout(() => setCopyMessage(null), 3000);
    } else {
      setCopyMessage('Failed to copy URL');
      setTimeout(() => setCopyMessage(null), 3000);
    }
  };

  const handleSort = async (field: SortField) => {
    const newDirection: 'asc' | 'desc' = 
      currentSort.field === field && currentSort.direction === 'asc' ? 'desc' : 'asc';
    
    setCurrentSort({ field, direction: newDirection });
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handleSortChange = (value: string) => {
    setSortBy(value);
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  // Render loading state
  if (loading && repositories.length === 0) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading repositories...</p>
      </div>
    );
  }

  // Render error state
  if (error) {
    return (
      <div className="error-message">
        <p>{error}</p>
        <button onClick={fetchRepositories} className="retry-btn">
          Retry
        </button>
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
          <h1>Your Repositories ({pagination.totalCount})</h1>
        </div>

        <RepositorySearch
          searchInput={searchInput}
          searchQuery={searchQuery}
          onSearchInputChange={setSearchInput}
          onSearch={handleSearch}
          onClearSearch={handleClearSearch}
        />

        <RepositoryControls
          sortBy={sortBy}
          perPage={pagination.perPage}
          onSortChange={handleSortChange}
          onPerPageChange={handlePerPageChange}
        />
      </div>

      {repositories.length === 0 ? (
        <div className="no-repositories">
          <h3>No repositories found</h3>
          <p>
            {searchQuery 
              ? `No repositories match "${searchQuery}".`
              : "You don't have any repositories yet."
            }
          </p>
        </div>
      ) : (
        <div className="repositories-table-container">
          <table className="repositories-table">
            <RepositoryTableHeader
              currentSort={currentSort}
              onSort={handleSort}
            />
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
      )}

      {repositories.length > 0 && (
        <RepositoryPagination
          pagination={pagination}
          onPageChange={handlePageChange}
          loading={loading}
        />
      )}
    </div>
  );
};

export default RepositoriesRefactored;
