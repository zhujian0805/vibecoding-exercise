// Shared types for pull request components
export interface PullRequestUser {
  login: string;
  avatar_url: string;
  html_url: string;
  id?: number;
}

export interface PullRequestRepository {
  name: string;
  full_name: string;
  html_url: string;
  id?: number;
}

export interface PullRequestBranch {
  ref: string;
  sha: string;
  label?: string;
}

export interface PullRequest {
  id: number;
  number: number;
  title: string;
  body?: string;
  state: 'open' | 'closed' | 'merged';
  user?: PullRequestUser;
  created_at?: string;
  updated_at?: string;
  closed_at?: string;
  merged_at?: string;
  html_url?: string;
  base?: PullRequestBranch;
  head?: PullRequestBranch;
  repository?: PullRequestRepository;
  draft: boolean;
  mergeable?: boolean;
  mergeable_state?: string;
  merged_by?: PullRequestUser;
  additions: number;
  deletions: number;
  changed_files: number;
  comments: number;
  review_comments: number;
  commits: number;
  assignees?: PullRequestUser[];
  requested_reviewers?: PullRequestUser[];
  labels?: Array<{
    id: number;
    name: string;
    color: string;
    description?: string;
  }>;
}

export interface PullRequestsResponse {
  pullrequests: PullRequest[];
  page: number;
  per_page: number;
  total_count: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
  search_query: string;
  sort: string;
  table_sort?: string;
  table_sort_direction?: string;
}

export type SortField = 'number' | 'title' | 'state' | 'author' | 'repository' | 'comments' | 'commits' | 'additions' | 'deletions' | 'updated_at' | 'created_at';
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

export interface ControlsState {
  sortBy: string;
  searchQuery: string;
  searchInput: string;
  currentSort: SortState;
  copyMessage: string | null;
}
