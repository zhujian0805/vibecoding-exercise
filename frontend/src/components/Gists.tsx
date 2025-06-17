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
  const [perPage, setPerPage] = useState(20);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [debugInfo, setDebugInfo] = useState<any>(null);
  const [copyMessage, setCopyMessage] = useState<string | null>(null);

  const fetchGists = async (pageNum: number = 1, search: string = '', sortBy: string = 'updated') => {
    setLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams({
        page: pageNum.toString(),
        per_page: perPage.toString(),
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
  }, [searchQuery, sort, perPage]);

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
      setPage(newPage);
      fetchGists(newPage, searchQuery, sort);
    }
  };

  const handleCopyGistUrl = async (cloneUrl: string, gistId: string) => {
    try {
      await navigator.clipboard.writeText(cloneUrl);
      setCopyMessage(`Clone URL copied for gist ${gistId}!`);
      setTimeout(() => setCopyMessage(null), 3000);
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
      setCopyMessage('Failed to copy clone URL');
      setTimeout(() => setCopyMessage(null), 3000);
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
      <div className="repositories">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading gists...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="repositories">
        <div className="error-message">
          {error}
          <button onClick={() => fetchGists(1, searchQuery, sort)} className="retry-btn">
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
          <h1>My Gists</h1>
        </div>
        
        {/* Compact Controls Section - All in one frame */}
        <div className="repositories-compact-controls">
          <form onSubmit={handleSearch} className="search-form">
            <div className="search-input-container">
              <input
                type="text"
                placeholder="Search gists by description, filename, or language..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="search-input"
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => setSearchQuery('')}
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
            </label>
          </div>
          
          <div className="control-group">
            <label>
              Items per page:
              <select 
                value={perPage} 
                onChange={(e) => {
                  const newPerPage = Number(e.target.value);
                  setPerPage(newPerPage);
                  setPage(1);
                  fetchGists(1, searchQuery, sort);
                }}
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

      {gists.length === 0 ? (
        <div className="no-repositories">
          <p>No gists found.</p>
          {searchQuery ? (
            <p>No gists match your search criteria. Try a different search term.</p>
          ) : (
            <p>You haven't created any gists yet. <a href="https://gist.github.com" target="_blank" rel="noopener noreferrer">Create your first gist</a></p>
          )}
        </div>
      ) : (
        <>
          {/* Pagination controls above the table */}
          <div className="pagination">
            <div className="pagination-info">
              Showing {((page - 1) * perPage) + 1} to {Math.min(page * perPage, totalCount)} of {totalCount} gists
              {totalPages > 1 && ` (Page ${page} of ${totalPages})`}
            </div>
            
            <div className="pagination-controls">
              <button 
                onClick={() => handlePageChange(1)}
                disabled={page === 1}
                className="page-btn first-btn"
              >
                First
              </button>
              <button 
                onClick={() => handlePageChange(Math.max(1, page - 1))}
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
                      onClick={() => handlePageChange(pageNum)}
                      className={`page-btn ${page === pageNum ? 'active' : ''}`}
                    >
                      {pageNum}
                    </button>
                  );
                })}
              </div>
              
              <button 
                onClick={() => handlePageChange(page + 1)}
                disabled={page === totalPages}
                className="page-btn"
              >
                Next
              </button>
              <button 
                onClick={() => handlePageChange(totalPages)}
                disabled={page === totalPages}
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
                  <th className="repo-name-cell">
                    <span>Description</span>
                  </th>
                  <th className="language-cell">
                    <span>Visibility</span>
                  </th>
                  <th className="stars-cell">
                    <span>Files</span>
                  </th>
                  <th className="forks-cell">
                    <span>Languages</span>
                  </th>
                  <th className="size-cell">
                    <span>💬</span>
                  </th>
                  <th className="updated-cell">
                    <span>Updated</span>
                  </th>
                  <th className="actions-cell">
                    <span>Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {gists.map((gist) => (
                  <tr key={gist.id}>
                    <td className="repo-name-cell">
                      <div className="repo-name-container">
                        <a 
                          href={gist.html_url || '#'} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="repo-name-link"
                        >
                          {gist.description || 'Untitled Gist'}
                        </a>
                        <div className="repo-badges">
                          <span className="badge">ID: {gist.id}</span>
                        </div>
                      </div>
                    </td>
                    
                    <td className="language-cell">
                      <div className="language-info">
                        <span className={`visibility-badge ${gist.public ? 'public' : 'private'}`}>
                          {gist.public ? 'Public' : 'Private'}
                        </span>
                      </div>
                    </td>
                    
                    <td className="stars-cell">
                      <div className="description-content">
                        <span className="stat-value">
                          {gist.file_count} {gist.file_count === 1 ? 'file' : 'files'}
                        </span>
                        {gist.files.length > 0 && (
                          <div className="topic-tags">
                            {gist.files.slice(0, 2).map((file, index) => (
                              <span key={index} className="topic-tag">
                                {file.filename}
                              </span>
                            ))}
                            {gist.files.length > 2 && (
                              <span className="topic-tag more">
                                +{gist.files.length - 2}
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    </td>
                    
                    <td className="forks-cell">
                      <span className="language-name">{getFileLanguages(gist.files)}</span>
                    </td>
                    
                    <td className="size-cell">
                      {gist.comments > 0 ? (
                        <span className="stat-value">{gist.comments}</span>
                      ) : (
                        <span className="no-data">—</span>
                      )}
                    </td>
                    
                    <td className="updated-cell">
                      <span className="updated-date">{formatDate(gist.updated_at)}</span>
                    </td>
                    
                    <td className="actions-cell">
                      <div className="repo-actions">
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
                            onClick={() => handleCopyGistUrl(gist.git_pull_url || '', gist.id)}
                            className="action-btn clone-btn"
                            title="Copy clone URL"
                          >
                            Copy
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
};

export default Gists;
