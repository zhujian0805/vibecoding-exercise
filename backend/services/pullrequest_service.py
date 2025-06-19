"""
Pull Request service for GitHub API operations using Repository pattern
"""
import time
import logging
from typing import List, Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial
from github import Github, GithubException
import requests
from models.pullrequest import PullRequest

logger = logging.getLogger(__name__)


class PullRequestRepository:
    """Repository pattern for GitHub pull request operations"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.github_client = Github(access_token)
    
    def get_total_pr_count(self) -> int:
        """Get total number of pull requests for the authenticated user"""
        try:
            # Use search API to get accurate count of all PRs for the user
            user = self.github_client.get_user()
            query = f"author:{user.login} type:pr"
            search_results = self.github_client.search_issues(query=query)
            return search_results.totalCount
        except Exception as e:
            logger.warning(f"Failed to get total PR count: {e}")
            return 0
    
    def fetch_prs_from_issues_api(self, page: int = 1, per_page: int = 100) -> List[dict]:
        """Fetch pull requests using GitHub Issues API (includes PRs)"""
        try:
            url = "https://api.github.com/user/issues"
            headers = {
                'Authorization': f'token {self.access_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            params = {
                'filter': 'all',
                'state': 'all',
                'pulls': 'true',  # This parameter ensures we only get PRs
                'page': page,
                'per_page': per_page,
                'sort': 'updated',
                'direction': 'desc'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            # Filter to only include pull requests (issues have pull_request field)
            issues = response.json()
            prs = [issue for issue in issues if 'pull_request' in issue]
            
            logger.debug(f"Fetched {len(prs)} PRs from page {page}")
            return prs
            
        except Exception as e:
            logger.error(f"Failed to fetch PRs from issues API page {page}: {e}")
            return []
    
    def fetch_pr_details(self, pr_data: dict) -> dict:
        """Fetch detailed PR information including stats"""
        try:
            pr_url = pr_data.get('pull_request', {}).get('url')
            if not pr_url:
                return pr_data
            
            headers = {
                'Authorization': f'token {self.access_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            response = requests.get(pr_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            detailed_pr = response.json()
            
            # Merge the detailed information with the original data
            pr_data.update({
                'additions': detailed_pr.get('additions', 0),
                'deletions': detailed_pr.get('deletions', 0),
                'changed_files': detailed_pr.get('changed_files', 0),
                'commits': detailed_pr.get('commits', 0),
                'mergeable': detailed_pr.get('mergeable'),
                'mergeable_state': detailed_pr.get('mergeable_state'),
                'merged_by': detailed_pr.get('merged_by'),
                'draft': detailed_pr.get('draft', False),
                'base': detailed_pr.get('base'),
                'head': detailed_pr.get('head'),
                'requested_reviewers': detailed_pr.get('requested_reviewers', []),
                'assignees': detailed_pr.get('assignees', [])
            })
            
            return pr_data
            
        except Exception as e:
            logger.warning(f"Failed to fetch PR details for {pr_data.get('number', 'unknown')}: {e}")
            return pr_data
    
    def get_all_pull_requests(self, user_id: int, max_prs: Optional[int] = None) -> List[PullRequest]:
        """Get all pull requests with parallel page fetching"""
        if max_prs is None:
            max_prs = min(self.get_total_pr_count(), 1000)  # Reasonable limit
        
        try:
            logger.debug(f"Fetching up to {max_prs} pull requests...")
            
            # Calculate pages needed
            per_page = 100
            pages_needed = min((max_prs + per_page - 1) // per_page, 10)  # Max 10 pages for safety
            
            all_prs = []
            
            # Fetch pages in parallel
            with ThreadPoolExecutor(max_workers=3) as executor:
                future_to_page = {
                    executor.submit(self.fetch_prs_from_issues_api, page, per_page): page 
                    for page in range(1, pages_needed + 1)
                }
                
                for future in as_completed(future_to_page):
                    page = future_to_page[future]
                    try:
                        prs_data = future.result()
                        all_prs.extend(prs_data)
                        logger.debug(f"Retrieved {len(prs_data)} PRs from page {page}")
                    except Exception as e:
                        logger.error(f"Failed to fetch page {page}: {e}")
            
            # Limit to requested number
            all_prs = all_prs[:max_prs]
            
            logger.debug(f"Fetched {len(all_prs)} PRs total, now enriching with details...")
            
            # Fetch detailed information for each PR (limited batch to avoid rate limits)
            detailed_prs = []
            batch_size = 20  # Process in smaller batches to be gentle on API
            
            for i in range(0, min(len(all_prs), 100), batch_size):  # Only detail first 100 PRs
                batch = all_prs[i:i + batch_size]
                
                with ThreadPoolExecutor(max_workers=5) as executor:
                    detailed_batch = list(executor.map(self.fetch_pr_details, batch))
                    detailed_prs.extend(detailed_batch)
                
                # Small delay between batches to be respectful of rate limits
                if i + batch_size < len(all_prs):
                    time.sleep(0.5)
            
            # Add remaining PRs without detailed info
            detailed_prs.extend(all_prs[len(detailed_prs):])
            
            # Convert to PullRequest objects
            pull_requests = []
            for pr_data in detailed_prs:
                try:
                    # Add repository information from the issue data
                    if 'repository' not in pr_data and 'repository_url' in pr_data:
                        # Extract repo info from repository_url
                        repo_url_parts = pr_data['repository_url'].split('/')
                        if len(repo_url_parts) >= 2:
                            owner = repo_url_parts[-2]
                            repo_name = repo_url_parts[-1]
                            pr_data['repository'] = {
                                'name': repo_name,
                                'full_name': f"{owner}/{repo_name}",
                                'html_url': f"https://github.com/{owner}/{repo_name}"
                            }
                    
                    pr = PullRequest.from_api_data(pr_data)
                    pull_requests.append(pr)
                except Exception as e:
                    logger.warning(f"Failed to convert PR data to PullRequest object: {e}")
                    continue
            
            logger.debug(f"Successfully converted {len(pull_requests)} PRs to objects")
            return pull_requests
            
        except Exception as e:
            logger.error(f"Failed to get all pull requests: {e}")
            return []


class PullRequestService:
    """Service for pull request operations with business logic"""
    
    def __init__(self, repository: PullRequestRepository):
        self.repository = repository
    
    def get_all_pull_requests(self, user_id: int) -> List[PullRequest]:
        """Get all pull requests for a user"""
        return self.repository.get_all_pull_requests(user_id)
    
    def filter_pull_requests(self, prs: List[PullRequest], search_query: Optional[str] = None) -> List[PullRequest]:
        """Filter pull requests based on search query"""
        if not search_query or not search_query.strip():
            return prs
        
        search_query = search_query.strip().lower()
        filtered_prs = []
        
        for pr in prs:
            # Search in title
            if search_query in (pr.title or '').lower():
                filtered_prs.append(pr)
                continue
            
            # Search in body
            if pr.body and search_query in pr.body.lower():
                filtered_prs.append(pr)
                continue
            
            # Search in author login
            if pr.user and search_query in (pr.user.login or '').lower():
                filtered_prs.append(pr)
                continue
            
            # Search in repository name
            if pr.repository and search_query in (pr.repository.name or '').lower():
                filtered_prs.append(pr)
                continue
            
            # Search in repository full name
            if pr.repository and search_query in (pr.repository.full_name or '').lower():
                filtered_prs.append(pr)
                continue
            
            # Search in PR number (convert to string)
            if search_query in str(pr.number):
                filtered_prs.append(pr)
                continue
        
        return filtered_prs
    
    def sort_pull_requests(self, prs: List[PullRequest], sort: str = 'updated', 
                          table_sort: Optional[str] = None, table_sort_direction: str = 'asc') -> List[PullRequest]:
        """Sort pull requests with various criteria"""
        
        # Table sorting takes precedence over regular sorting
        if table_sort:
            sort_key = table_sort
            reverse = table_sort_direction == 'desc'
        else:
            sort_key = sort
            reverse = sort in ['updated', 'created']  # Default to desc for date fields
        
        try:
            if sort_key == 'updated':
                prs.sort(key=lambda pr: pr.updated_at or '', reverse=reverse)
            elif sort_key == 'created':
                prs.sort(key=lambda pr: pr.created_at or '', reverse=reverse)
            elif sort_key == 'title':
                prs.sort(key=lambda pr: (pr.title or '').lower(), reverse=reverse)
            elif sort_key == 'number':
                prs.sort(key=lambda pr: pr.number, reverse=reverse)
            elif sort_key == 'state':
                prs.sort(key=lambda pr: pr.state, reverse=reverse)
            elif sort_key == 'author':
                prs.sort(key=lambda pr: (pr.user.login if pr.user else '').lower(), reverse=reverse)
            elif sort_key == 'repository':
                prs.sort(key=lambda pr: (pr.repository.name if pr.repository else '').lower(), reverse=reverse)
            elif sort_key == 'comments':
                prs.sort(key=lambda pr: pr.comments, reverse=reverse)
            elif sort_key == 'commits':
                prs.sort(key=lambda pr: pr.commits, reverse=reverse)
            elif sort_key == 'additions':
                prs.sort(key=lambda pr: pr.additions, reverse=reverse)
            elif sort_key == 'deletions':
                prs.sort(key=lambda pr: pr.deletions, reverse=reverse)
            else:
                # Default sort by updated date
                prs.sort(key=lambda pr: pr.updated_at or '', reverse=True)
                
        except Exception as e:
            logger.warning(f"Failed to sort PRs by {sort_key}: {e}")
            # Fallback to default sorting
            prs.sort(key=lambda pr: pr.updated_at or '', reverse=True)
        
        return prs
    
    def paginate_pull_requests(self, prs: List[PullRequest], page: int = 1, 
                             per_page: int = 30) -> tuple[List[PullRequest], dict]:
        """Paginate pull requests and return pagination info"""
        per_page = min(per_page, 100)  # Limit max per page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        paginated_prs = prs[start_idx:end_idx]
        
        pagination_info = {
            'page': page,
            'per_page': per_page,
            'total_count': len(prs),
            'total_pages': (len(prs) + per_page - 1) // per_page if len(prs) > 0 else 1,
            'has_next': end_idx < len(prs),
            'has_prev': page > 1
        }
        
        return paginated_prs, pagination_info
