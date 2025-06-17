import React from 'react';
import { PaginationState } from './types';

interface RepositoryPaginationProps {
  pagination: PaginationState;
  onPageChange: (page: number) => void;
  loading: boolean;
}

const RepositoryPagination: React.FC<RepositoryPaginationProps> = ({
  pagination,
  onPageChange,
  loading,
}) => {
  const { page, totalPages, totalCount, perPage, hasNext, hasPrev } = pagination;

  const renderPageNumbers = () => {
    const pages = [];
    const maxVisiblePages = 5;
    let startPage = Math.max(1, page - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

    if (endPage - startPage + 1 < maxVisiblePages) {
      startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }

    // First page
    if (startPage > 1) {
      pages.push(
        <button
          key={1}
          onClick={() => onPageChange(1)}
          className="page-btn first-btn"
          disabled={loading}
        >
          1
        </button>
      );
      if (startPage > 2) {
        pages.push(<span key="ellipsis1">...</span>);
      }
    }

    // Page numbers
    for (let i = startPage; i <= endPage; i++) {
      pages.push(
        <button
          key={i}
          onClick={() => onPageChange(i)}
          className={`page-btn ${i === page ? 'active' : ''}`}
          disabled={loading}
        >
          {i}
        </button>
      );
    }

    // Last page
    if (endPage < totalPages) {
      if (endPage < totalPages - 1) {
        pages.push(<span key="ellipsis2">...</span>);
      }
      pages.push(
        <button
          key={totalPages}
          onClick={() => onPageChange(totalPages)}
          className="page-btn last-btn"
          disabled={loading}
        >
          {totalPages}
        </button>
      );
    }

    return pages;
  };

  const startItem = (page - 1) * perPage + 1;
  const endItem = Math.min(page * perPage, totalCount);

  return (
    <div className="pagination">
      <div className="pagination-info">
        Showing {startItem}-{endItem} of {totalCount} repositories
      </div>
      
      <div className="pagination-controls">
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={!hasPrev || loading}
          className="page-btn"
        >
          Previous
        </button>
        
        <div className="page-numbers">
          {renderPageNumbers()}
        </div>
        
        <button
          onClick={() => onPageChange(page + 1)}
          disabled={!hasNext || loading}
          className="page-btn"
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default RepositoryPagination;
