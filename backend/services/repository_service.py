"""
Repository service for GitHub API operations using Repository pattern
"""
import os
import logging
import time
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial
import requests
from github import Github, GithubException
from models.repository import Repository

logger = logging.getLogger(__name__)


class RepositoryRepository:
    """Repository pattern for GitHub repository operations"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.github_client = Github(access_token)
    
    def get_total_repo_count(self) -> int:
        """Get total number of repositories for the authenticated user"""
        try:
            user = self.github_client.get_user()
            repo_list = user.get_repos()
            return repo_list.totalCount
        except Exception as e:
            logger.warning(f"Failed to get total repo count: {e}")
            # Fallback to direct API call
            try:
                user = self.github_client.get_user()
                return user.public_repos
            except Exception:
                return 0
    
    def fetch_repos_page(self, page: int, per_page: int = 100) -> List[dict]:
        """Fetch a single page of repositories using direct API call"""
        try:
            url = f"https://api.github.com/user/repos"
            headers = {
                'Authorization': f'token {self.access_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            params = {
                'visibility': 'all',
                'sort': 'updated',
                'per_page': per_page,
                'page': page
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to fetch repos page {page}: {e}")
            return []
    
    def get_all_repositories(self, user_id: int, max_repos: int = None) -> List[Repository]:
        """Get all repositories with parallel page fetching"""
        if max_repos is None:
            max_repos = int(os.environ.get('MAX_REPOS_FETCH', '2000'))
        
        try:
            # Get total count and calculate pages needed
            total_repos = self.get_total_repo_count()
            actual_limit = min(total_repos, max_repos)
            
            per_page = 100  # GitHub's maximum per page
            num_pages = (actual_limit + per_page - 1) // per_page  # Ceiling division
            
            logger.debug(f"Fetching {actual_limit} repositories across {num_pages} pages")
            
            # Fetch all pages in parallel
            all_repo_data = []
            max_workers = min(10, num_pages)  # Limit concurrent API calls
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all page fetch tasks
                future_to_page = {
                    executor.submit(self.fetch_repos_page, page + 1, per_page): page + 1
                    for page in range(num_pages)
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_page):
                    page_num = future_to_page[future]
                    try:
                        page_data = future.result(timeout=30)
                        if page_data:
                            all_repo_data.extend(page_data)
                            logger.debug(f"Successfully fetched page {page_num} with {len(page_data)} repos")
                    except Exception as e:
                        logger.error(f"Failed to fetch page {page_num}: {e}")
            
            logger.debug(f"Fetched {len(all_repo_data)} repositories from {num_pages} pages")
            
            # Convert to Repository objects in parallel
            repositories = []
            if all_repo_data:
                max_workers = min(200, len(all_repo_data))
                
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    future_to_repo = {
                        executor.submit(Repository.from_api_data, repo_data): repo_data 
                        for repo_data in all_repo_data
                    }
                    
                    for future in as_completed(future_to_repo):
                        repo_data = future_to_repo[future]
                        try:
                            repository = future.result(timeout=30)
                            if repository:
                                repositories.append(repository)
                        except Exception as e:
                            logger.error(f"Failed to process repo {repo_data.get('name', 'unknown')}: {e}")
            
            logger.debug(f"Successfully processed {len(repositories)} repositories")
            return repositories
            
        except Exception as e:
            logger.error(f"Failed to fetch repositories: {e}")
            raise


class RepositoryService:
    """Service for repository operations with business logic"""
    
    def __init__(self, repository: RepositoryRepository):
        self.repository = repository
    
    def get_all_repositories(self, user_id: int) -> List[Repository]:
        """Get all repositories for a user"""
        return self.repository.get_all_repositories(user_id)
    
    def filter_repositories(self, repositories: List[Repository], search_query: str = None) -> List[Repository]:
        """Filter repositories based on search query"""
        if not search_query or not search_query.strip():
            return repositories
        
        search_query = search_query.strip().lower()
        filtered_repos = []
        
        for repo in repositories:
            # Search in name, description, and language
            if (search_query in repo.name.lower() or
                (repo.description and search_query in repo.description.lower()) or
                (repo.language and search_query in repo.language.lower()) or
                any(search_query in topic.lower() for topic in repo.topics)):
                filtered_repos.append(repo)
        
        return filtered_repos
    
    def sort_repositories(self, repositories: List[Repository], sort: str = 'updated', 
                         table_sort: str = None, table_sort_direction: str = 'asc') -> List[Repository]:
        """Sort repositories with various criteria"""
        
        # Table sorting takes precedence over regular sorting
        if table_sort:
            sort_key = table_sort
            reverse = table_sort_direction == 'desc'
        else:
            sort_key = sort
            reverse = True  # Default to descending for most sorts
        
        try:
            if sort_key == 'name':
                repositories.sort(key=lambda r: r.name.lower(), reverse=reverse)
            elif sort_key == 'language':
                repositories.sort(key=lambda r: (r.language or '').lower(), reverse=reverse)
            elif sort_key == 'stargazers_count' or sort_key == 'stars':
                repositories.sort(key=lambda r: r.stargazers_count, reverse=reverse)
            elif sort_key == 'forks_count' or sort_key == 'forks':
                repositories.sort(key=lambda r: r.forks_count, reverse=reverse)
            elif sort_key == 'size':
                repositories.sort(key=lambda r: r.size, reverse=reverse)
            elif sort_key == 'created_at' or sort_key == 'created':
                repositories.sort(key=lambda r: r.created_at or '', reverse=reverse)
            elif sort_key == 'updated_at' or sort_key == 'updated':
                repositories.sort(key=lambda r: r.updated_at or '', reverse=reverse)
            elif sort_key == 'pushed_at' or sort_key == 'pushed':
                repositories.sort(key=lambda r: r.pushed_at or '', reverse=reverse)
            else:
                # Default to updated_at
                repositories.sort(key=lambda r: r.updated_at or '', reverse=True)
                
        except Exception as e:
            logger.warning(f"Failed to sort repositories by {sort_key}: {e}")
            # Fallback to name sorting
            repositories.sort(key=lambda r: r.name.lower())
        
        return repositories
    
    def paginate_repositories(self, repositories: List[Repository], page: int = 1, 
                            per_page: int = 30) -> tuple[List[Repository], dict]:
        """Paginate repositories and return pagination info"""
        per_page = min(per_page, 100)  # Limit max per page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        paginated_repos = repositories[start_idx:end_idx]
        
        pagination_info = {
            'page': page,
            'per_page': per_page,
            'total_count': len(repositories),
            'total_pages': (len(repositories) + per_page - 1) // per_page if len(repositories) > 0 else 1,
            'has_next': end_idx < len(repositories),
            'has_prev': page > 1
        }
        
        return paginated_repos, pagination_info
