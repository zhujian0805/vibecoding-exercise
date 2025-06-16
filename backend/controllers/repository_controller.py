"""
Repository controller with proper error handling and caching
"""
import logging
import time
from flask import Blueprint, request, session, jsonify
from github import Github
from services.repository_service import RepositoryService, RepositoryRepository
from services.cache_service import CacheManager
from config import settings

logger = logging.getLogger(__name__)


class RepositoryController:
    """Controller for repository-related endpoints"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.blueprint = Blueprint('repositories', __name__)
        self._register_routes()
    
    def _register_routes(self):
        """Register all repository routes"""
        self.blueprint.add_url_rule('/api/repositories', 'repositories', self.repositories, methods=['GET'])
        self.blueprint.add_url_rule('/api/debug/simple-repos', 'debug_simple_repos', self.debug_simple_repos, methods=['GET'])
    
    def _check_authentication(self):
        """Check if user is authenticated and return user data and access token"""
        if 'user' not in session:
            logger.debug("User not authenticated")
            return None, None, jsonify({'error': 'Not authenticated'}), 401
        
        access_token = session.get('access_token')
        if not access_token:
            logger.debug("No access token found")
            return None, None, jsonify({'error': 'No access token'}), 401
        
        user = session.get('user', {})
        return user, access_token, None, None
    
    def _check_rate_limit(self, access_token: str, user_id: int) -> bool:
        """Check GitHub API rate limit with caching"""
        rate_limit_cache_key = self.cache_manager.generate_cache_key('rate_limit', user_id)
        rate_limit_ok = self.cache_manager.get(rate_limit_cache_key)
        
        if rate_limit_ok is None:
            logger.debug("Checking rate limit...")
            try:
                github_client = Github(access_token)
                rate_limit = github_client.get_rate_limit()
                # Consider rate limit OK if we have at least 100 requests remaining
                rate_limit_ok = rate_limit.core.remaining >= 100
                
                # Cache the result for 1 minute
                self.cache_manager.set(rate_limit_cache_key, rate_limit_ok, timeout=60)
                logger.debug(f"Rate limit check: {rate_limit.core.remaining} remaining")
            except Exception as e:
                logger.warning(f"Failed to check rate limit: {e}")
                rate_limit_ok = True  # Assume OK if check fails
        else:
            logger.debug("Rate limit check cached")
        
        return rate_limit_ok
    
    def repositories(self):
        """Get repositories with filtering, sorting, and pagination"""
        start_time = time.time()
        logger.debug(f"/api/repositories called from {request.remote_addr}")
        
        # Check authentication
        user, access_token, error_response, error_code = self._check_authentication()
        if error_response:
            return error_response, error_code
        
        user_id = user.get('id')
        user_login = user.get('login', 'unknown')
        logger.debug(f"User: {user_login}")
        
        try:
            # Get parameters
            sort = request.args.get('sort', 'updated')
            search_query = request.args.get('search', '').strip()
            page = int(request.args.get('page', 1))
            per_page = min(int(request.args.get('per_page', 30)), 100)
            
            # Table sorting parameters
            table_sort = request.args.get('table_sort')
            table_sort_direction = request.args.get('table_sort_direction', 'asc')
            
            logger.debug(f"Parameters - sort: {sort}, search: '{search_query}', page: {page}, "
                        f"per_page: {per_page}, table_sort: {table_sort}, table_sort_direction: {table_sort_direction}")
            
            # Check rate limit
            if not self._check_rate_limit(access_token, user_id):
                return jsonify({'error': 'Rate limit too low, please try again later'}), 429
            
            logger.debug("Fetching repositories using cached method...")
            fetch_start = time.time()
            
            # Get all repositories from cache or API
            cache_key = self.cache_manager.generate_cache_key('repos', user_id)
            cached_repos = self.cache_manager.get(cache_key)
            
            if cached_repos is not None:
                logger.debug(f"Repository cache hit for user {user_id}")
                repositories = cached_repos
            else:
                logger.debug(f"Repository cache miss for user {user_id}, fetching from API")
                
                # Create repository service and fetch data
                repo_repository = RepositoryRepository(access_token)
                repo_service = RepositoryService(repo_repository)
                
                repositories = repo_service.get_all_repositories(user_id)
                
                # Cache the repositories for 1 hour
                self.cache_manager.set(cache_key, repositories, timeout=3600)
                logger.debug(f"Cached {len(repositories)} repositories for user {user_id}")
            
            # Create repository service for business logic operations
            repo_repository = RepositoryRepository(access_token)
            repo_service = RepositoryService(repo_repository)
            
            # Apply search filter if needed
            if search_query:
                repositories = repo_service.filter_repositories(repositories, search_query)
            
            # Apply sorting
            repositories = repo_service.sort_repositories(
                repositories, sort=sort, table_sort=table_sort, 
                table_sort_direction=table_sort_direction
            )
            
            # Apply pagination
            paginated_repos, pagination_info = repo_service.paginate_repositories(
                repositories, page=page, per_page=per_page
            )
            
            # Convert to dictionaries for JSON response
            repo_dicts = [repo.to_dict() for repo in paginated_repos]
            
            fetch_time = time.time() - fetch_start
            total_time = time.time() - start_time
            
            logger.debug(f"Processed {len(paginated_repos)} repositories in {fetch_time:.2f}s")
            logger.debug(f"Total processing time: {total_time:.2f}s")
            
            result = {
                'repositories': repo_dicts,
                'search_query': search_query,
                'table_sort': table_sort,
                'table_sort_direction': table_sort_direction,
                'debug_info': {
                    'processing_time': total_time,
                    'fetch_time': fetch_time,
                    'repos_total': len(repositories),
                    'repos_returned': len(paginated_repos),
                    'cache_enabled': True,
                    'single_cache_strategy': True,
                    'table_sort_applied': bool(table_sort)
                },
                **pagination_info
            }
            
            logger.debug(f"Returning {len(paginated_repos)} repositories "
                        f"(page {pagination_info['page']}/{pagination_info['total_pages']})")
            return jsonify(result)
            
        except Exception as e:
            error_msg = f'Failed to fetch repositories: {str(e)}'
            logger.error(f"Exception in repositories endpoint: {error_msg}")
            return jsonify({'error': error_msg}), 500
    
    def debug_simple_repos(self):
        """Debug endpoint to test simple repository fetch"""
        user, access_token, error_response, error_code = self._check_authentication()
        if error_response:
            return error_response, error_code
        
        try:
            start_time = time.time()
            github_client = Github(access_token)
            user_obj = github_client.get_user()
            
            # Use simple auto-paginated approach, but limit to 5 repos
            simple_repos = []
            for repo in user_obj.get_repos(visibility='all'):
                simple_repos.append({
                    'name': repo.name,
                    'full_name': repo.full_name,
                    'private': repo.private,
                    'clone_url': repo.clone_url
                })
                if len(simple_repos) >= 5:
                    break
            
            end_time = time.time()
            return jsonify({
                'repositories': simple_repos,
                'count': len(simple_repos),
                'processing_time': end_time - start_time
            })
            
        except Exception as e:
            return jsonify({'error': f'Failed to fetch simple repos: {str(e)}'}), 500
