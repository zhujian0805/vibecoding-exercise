import React from 'react';

interface PullRequestPaginationProps {
  page: number;
  perPage: number;
  totalPages: number;
  totalCount: number;
  hasNext: boolean;
  hasPrev: boolean;
  onPageChange: (page: number) => void;
  onPerPageChange: (perPage: number) => void;
  loading: boolean;
}

const PullRequestPagination: React.FC<PullRequestPaginationProps> = ({
  page,
  perPage,
  totalPages,
  totalCount,
  hasNext,
  hasPrev,
  onPageChange,
  onPerPageChange,
  loading
}) => {
  const startItem = totalCount === 0 ? 0 : (page - 1) * perPage + 1;
  const endItem = Math.min(page * perPage, totalCount);

  const getPageNumbers = (): number[] => {
    const pages: number[] = [];
    const showPages = 5; // Number of page buttons to show
    const halfShow = Math.floor(showPages / 2);
    
    let startPage = Math.max(1, page - halfShow);
    let endPage = Math.min(totalPages, page + halfShow);
    
    // Adjust if we're near the beginning or end
    if (endPage - startPage + 1 < showPages) {
      if (startPage === 1) {
        endPage = Math.min(totalPages, startPage + showPages - 1);
      } else {
        startPage = Math.max(1, endPage - showPages + 1);
      }
    }
    
    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }
    
    return pages;
  };

  if (totalCount === 0) {
    return null;
  }

  return (
    <div className="pagination-container">
      <div className="pagination-info">
        <span>
          Showing {startItem} to {endItem} of {totalCount} pull requests
        </span>
      </div>
      
      <div className="pagination-controls">
        <div className="per-page-selector">
          <label htmlFor="per-page-select">Show:</label>
          <select
            id="per-page-select"
            value={perPage}
            onChange={(e) => onPerPageChange(Number(e.target.value))}
            disabled={loading}
            className="per-page-select"
          >
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={30}>30</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
          </select>
          <span>per page</span>
        </div>
        
        <div className="page-navigation">
          <button
            onClick={() => onPageChange(1)}
            disabled={!hasPrev || loading}
            className="pagination-btn first-btn"
            title="First page"
          >
            ⟪
          </button>
          
          <button
            onClick={() => onPageChange(page - 1)}
            disabled={!hasPrev || loading}
            className="pagination-btn prev-btn"
            title="Previous page"
          >
            ⟨
          </button>
          
          {getPageNumbers().map((pageNum) => (
            <button
              key={pageNum}
              onClick={() => onPageChange(pageNum)}
              disabled={loading}
              className={`pagination-btn page-btn ${pageNum === page ? 'active' : ''}`}
            >
              {pageNum}
            </button>
          ))}
          
          <button
            onClick={() => onPageChange(page + 1)}
            disabled={!hasNext || loading}
            className="pagination-btn next-btn"
            title="Next page"
          >
            ⟩
          </button>
          
          <button
            onClick={() => onPageChange(totalPages)}
            disabled={!hasNext || loading}
            className="pagination-btn last-btn"
            title="Last page"
          >
            ⟫
          </button>
        </div>
      </div>
      
      <div className="pagination-summary">
        <span>
          Page {page} of {totalPages}
        </span>
      </div>
    </div>
  );
};

export default PullRequestPagination;
