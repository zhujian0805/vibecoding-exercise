// Shared types for repository components
export interface Repository {
  id: number;
  name: string;
  full_name: string;
  description: string;
  private: boolean;
  html_url: string;
  clone_url: string;
  ssh_url: string;
  language: string;
  stargazers_count: number;
  watchers_count: number;
  forks_count: number;
  size: number;
  default_branch: string;
  created_at: string;
  updated_at: string;
  pushed_at: string;
  archived: boolean;
  disabled: boolean;
  fork: boolean;
  topics: string[];
  visibility: string;
}

export interface RepositoriesResponse {
  repositories: Repository[];
  page: number;
  per_page: number;
  total_count: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
  search_query: string;
  table_sort?: string;
  table_sort_direction?: string;
}

export type SortField = 'name' | 'language' | 'stargazers_count' | 'forks_count' | 'size' | 'updated_at';
export type SortDirection = 'asc' | 'desc';

export interface SortState {
  field: SortField | null;
  direction: SortDirection;
}

export interface PaginationState {
  page: number;
  perPage: number;
  totalPages: number;
  totalCount: number;
  hasNext: boolean;
  hasPrev: boolean;
}
