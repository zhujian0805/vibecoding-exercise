import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface GistFile {
  filename: string;
  type: string;
  language: string | null;
  raw_url: string | null;
  size: number;
  truncated: boolean;
  content: string | null;
}

interface Gist {
  id: string;
  description: string | null;
  public: boolean;
  html_url: string | null;
  git_pull_url: string | null;
  git_push_url: string | null;
  created_at: string | null;
  updated_at: string | null;
  comments: number;
  files: GistFile[];
  owner: {
    login: string | null;
    avatar_url: string | null;
  };
  truncated: boolean;
  file_count: number;
}

interface GistsResponse {
  gists: Gist[];
  search_query: string;
  table_sort: string | null;
  table_sort_direction: string;
  page: number;
  per_page: number;
  total_count: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
  debug_info: {
    processing_time: number;
    fetch_time: number;
    gists_total: number;
    gists_returned: number;
    cache_enabled: boolean;
    single_cache_strategy: boolean;
    table_sort_applied: boolean;
  };
}

const API_BASE_URL = 'http://localhost:5000';

const Gists: React.FC = () => {
  const [gists, setGists] = useState<Gist[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [sort, setSort] = useState('updated');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [debugInfo, setDebugInfo] = useState<any>(null);

  const fetchGists = async (pageNum: number = 1, search: string = '', sortBy: string = 'updated') => {
    setLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams({
        page: pageNum.toString(),
        per_page: '20',
        sort: sortBy,
        search: search.trim()
      });

      const response = await axios.get<GistsResponse>(`${API_BASE_URL}/api/gists?${params}`);
      const data = response.data;
      
      setGists(data.gists);
      setPage(data.page);
      setTotalPages(data.total_pages);
      setTotalCount(data.total_count);
      setDebugInfo(data.debug_info);
      
    } catch (err: any) {
      console.error('Error fetching gists:', err);
      setError(err.response?.data?.error || 'Failed to fetch gists');
      setGists([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGists(1, searchQuery, sort);
  }, [searchQuery, sort]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchGists(1, searchQuery, sort);
  };

  const handleSort = (newSort: string) => {
    setSort(newSort);
    setPage(1);
    fetchGists(1, searchQuery, newSort);
  };

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      fetchGists(newPage, searchQuery, sort);
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  const getFileLanguages = (files: GistFile[]) => {
    const languages = files
      .map(file => file.language)
      .filter(lang => lang && lang !== null)
      .filter((lang, index, arr) => arr.indexOf(lang) === index); // Remove duplicates
    
    return languages.length > 0 ? languages.join(', ') : 'Text';
  };

  if (loading) {
    return (
      <div className="gists-container">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading gists...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="gists-container">
        <div className="error">
          <h3>Error</h3>
          <p>{error}</p>
          <button onClick={() => fetchGists(1, searchQuery, sort)}>
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="gists-container">
      <div className="gists-header">
        <h2>My Gists</h2>
        <p>Your GitHub gists ({totalCount} total)</p>
      </div>

      {/* Search and Controls */}
      <div className="gists-controls">
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            placeholder="Search gists by description, filename, or language..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
          <button type="submit" className="search-button">
            Search
          </button>
        </form>

        <div className="sort-controls">
          <label htmlFor="sort-select">Sort by:</label>
          <select
            id="sort-select"
            value={sort}
            onChange={(e) => handleSort(e.target.value)}
            className="sort-select"
          >
            <option value="updated">Last Updated</option>
            <option value="created">Created Date</option>
            <option value="description">Description</option>
            <option value="comments">Comments</option>
            <option value="files">File Count</option>
            <option value="public">Visibility</option>
          </select>
        </div>
      </div>

      {/* Gists List */}
      {gists.length === 0 ? (
        <div className="no-gists">
          <h3>No gists found</h3>
          {searchQuery ? (
            <p>No gists match your search criteria. Try a different search term.</p>
          ) : (
            <p>You haven't created any gists yet. <a href="https://gist.github.com" target="_blank" rel="noopener noreferrer">Create your first gist</a></p>
          )}
        </div>
      ) : (
        <>
          <div className="gists-grid">
            {gists.map((gist) => (
              <div key={gist.id} className="gist-card">
                <div className="gist-header">
                  <h3 className="gist-title">
                    <a href={gist.html_url || '#'} target="_blank" rel="noopener noreferrer">
                      {gist.description || 'Untitled Gist'}
                    </a>
                  </h3>
                  <div className="gist-visibility">
                    <span className={`visibility-badge ${gist.public ? 'public' : 'private'}`}>
                      {gist.public ? 'Public' : 'Private'}
                    </span>
                  </div>
                </div>

                <div className="gist-meta">
                  <div className="gist-stats">
                    <span className="stat">
                      <strong>{gist.file_count}</strong> {gist.file_count === 1 ? 'file' : 'files'}
                    </span>
                    {gist.comments > 0 && (
                      <span className="stat">
                        <strong>{gist.comments}</strong> {gist.comments === 1 ? 'comment' : 'comments'}
                      </span>
                    )}
                  </div>
                  
                  <div className="gist-languages">
                    <strong>Languages:</strong> {getFileLanguages(gist.files)}
                  </div>
                </div>

                <div className="gist-files">
                  <strong>Files:</strong>
                  <ul className="file-list">
                    {gist.files.slice(0, 3).map((file, index) => (
                      <li key={index} className="file-item">
                        <span className="filename">{file.filename}</span>
                        {file.language && (
                          <span className="file-language">({file.language})</span>
                        )}
                      </li>
                    ))}
                    {gist.files.length > 3 && (
                      <li className="file-item more-files">
                        +{gist.files.length - 3} more files
                      </li>
                    )}
                  </ul>
                </div>

                <div className="gist-dates">
                  <div className="date-info">
                    <strong>Created:</strong> {formatDate(gist.created_at)}
                  </div>
                  <div className="date-info">
                    <strong>Updated:</strong> {formatDate(gist.updated_at)}
                  </div>
                </div>

                <div className="gist-actions">
                  <a href={gist.html_url || '#'} target="_blank" rel="noopener noreferrer" className="action-link">
                    View on GitHub
                  </a>
                  {gist.git_pull_url && (
                    <button
                      onClick={() => navigator.clipboard.writeText(gist.git_pull_url || '')}
                      className="action-button"
                      title="Copy clone URL"
                    >
                      Copy Clone URL
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="pagination">
              <button
                onClick={() => handlePageChange(page - 1)}
                disabled={page === 1}
                className="pagination-button"
              >
                Previous
              </button>
              
              <div className="pagination-info">
                Page {page} of {totalPages} ({totalCount} total gists)
              </div>
              
              <button
                onClick={() => handlePageChange(page + 1)}
                disabled={page === totalPages}
                className="pagination-button"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}

      {/* Debug Info */}
      {debugInfo && (
        <div className="debug-info">
          <h4>Debug Information</h4>
          <div className="debug-stats">
            <span>Processing Time: {debugInfo.processing_time?.toFixed(3)}s</span>
            <span>Fetch Time: {debugInfo.fetch_time?.toFixed(3)}s</span>
            <span>Cache Enabled: {debugInfo.cache_enabled ? 'Yes' : 'No'}</span>
            <span>Total Gists: {debugInfo.gists_total}</span>
            <span>Returned: {debugInfo.gists_returned}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default Gists;
