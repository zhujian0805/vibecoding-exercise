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
        <h2>Gists</h2>
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
          {/* Pagination controls above the table */}
          {totalPages > 1 && (
            <div className="pagination">
              <div className="pagination-info">
                Showing {((page - 1) * 20) + 1} to {Math.min(page * 20, totalCount)} of {totalCount} gists
                {totalPages > 1 && ` (Page ${page} of ${totalPages})`}
              </div>
              
              <div className="pagination-controls">
                <button 
                  onClick={() => setPage(1)}
                  disabled={page === 1}
                  className="page-btn first-btn"
                >
                  First
                </button>
                <button 
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
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
                  disabled={page === totalPages}
                  className="page-btn"
                >
                  Next
                </button>
                <button 
                  onClick={() => setPage(totalPages)}
                  disabled={page === totalPages}
                  className="page-btn last-btn"
                >
                  Last
                </button>
              </div>
            </div>
          )}

          <div className="gists-table-container">
            <table className="gists-table">
              <thead>
                <tr>
                  <th className="gist-description-cell">
                    <span>Description</span>
                  </th>
                  <th className="gist-visibility-cell">
                    <span>Visibility</span>
                  </th>
                  <th className="gist-files-cell">
                    <span>Files</span>
                  </th>
                  <th className="gist-languages-cell">
                    <span>Languages</span>
                  </th>
                  <th className="gist-comments-cell">
                    <span>💬</span>
                  </th>
                  <th className="gist-updated-cell">
                    <span>Updated</span>
                  </th>
                  <th className="gist-actions-cell">
                    <span>Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {gists.map((gist) => (
                  <tr key={gist.id}>
                    <td className="gist-description-cell">
                      <div className="gist-description-container">
                        <a 
                          href={gist.html_url || '#'} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="gist-description-link"
                        >
                          {gist.description || 'Untitled Gist'}
                        </a>
                        <div className="gist-id">
                          ID: {gist.id}
                        </div>
                      </div>
                    </td>
                    <td className="gist-visibility-cell">
                      <span className={`visibility-badge ${gist.public ? 'public' : 'private'}`}>
                        {gist.public ? 'Public' : 'Private'}
                      </span>
                    </td>
                    <td className="gist-files-cell">
                      <div className="files-info">
                        <span className="file-count">
                          {gist.file_count} {gist.file_count === 1 ? 'file' : 'files'}
                        </span>
                        {gist.files.length > 0 && (
                          <div className="file-list-compact">
                            {gist.files.slice(0, 2).map((file, index) => (
                              <span key={index} className="file-name-compact">
                                {file.filename}
                              </span>
                            ))}
                            {gist.files.length > 2 && (
                              <span className="more-files-compact">
                                +{gist.files.length - 2} more
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="gist-languages-cell">
                      <div className="languages-info">
                        {getFileLanguages(gist.files)}
                      </div>
                    </td>
                    <td className="gist-comments-cell">
                      {gist.comments > 0 ? (
                        <span className="comment-count">{gist.comments}</span>
                      ) : (
                        <span className="no-comments">-</span>
                      )}
                    </td>
                    <td className="gist-updated-cell">
                      <div className="date-info">
                        <div className="updated-date">
                          {formatDate(gist.updated_at)}
                        </div>
                        <div className="created-date">
                          Created: {formatDate(gist.created_at)}
                        </div>
                      </div>
                    </td>
                    <td className="gist-actions-cell">
                      <div className="action-buttons">
                        <a 
                          href={gist.html_url || '#'} 
                          target="_blank" 
                          rel="noopener noreferrer" 
                          className="action-btn view-btn"
                          title="View on GitHub"
                        >
                          View
                        </a>
                        {gist.git_pull_url && (
                          <button
                            onClick={() => navigator.clipboard.writeText(gist.git_pull_url || '')}
                            className="action-btn copy-btn"
                            title="Copy clone URL"
                          >
                            Copy URL
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination controls below the table */}
          {totalPages > 1 && (
            <div className="pagination">
              <div className="pagination-info">
                Showing {((page - 1) * 20) + 1} to {Math.min(page * 20, totalCount)} of {totalCount} gists
                {totalPages > 1 && ` (Page ${page} of ${totalPages})`}
              </div>
              
              <div className="pagination-controls">
                <button 
                  onClick={() => setPage(1)}
                  disabled={page === 1}
                  className="page-btn first-btn"
                >
                  First
                </button>
                <button 
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
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
                  disabled={page === totalPages}
                  className="page-btn"
                >
                  Next
                </button>
                <button 
                  onClick={() => setPage(totalPages)}
                  disabled={page === totalPages}
                  className="page-btn last-btn"
                >
                  Last
                </button>
              </div>
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
