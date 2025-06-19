"""
Pull Request controller with proper error handling and caching
"""
import time
import logging
from flask import Blueprint, request, session, jsonify
from github import Github
from services.pullrequest_service import PullRequestService, PullRequestRepository
from services.cache_service import CacheManager

logger = logging.getLogger(__name__)


class PullRequestController:
    """Controller for pull request-related endpoints"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.blueprint = Blueprint('pullrequests', __name__)
        self._register_routes()
    
    def _register_routes(self):
        """Register all pull request routes"""
        self.blueprint.add_url_rule('/api/pullrequests', 'pullrequests', self.pullrequests, methods=['GET'])
        self.blueprint.add_url_rule('/api/debug/simple-pullrequests', 'debug_simple_pullrequests', self.debug_simple_pullrequests, methods=['GET'])
    
    def _check_authentication(self):
        """Check if user is authenticated and return user data and access token"""
        if 'user' not in session:
            logger.debug("User not authenticated")
            return None, None, jsonify({'error': 'Authentication required'}), 401
        
        access_token = session.get('access_token')
        if not access_token:
            logger.debug("No access token found")
            return None, None, jsonify({'error': 'Access token required'}), 401
        
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
                remaining = rate_limit.core.remaining
                rate_limit_ok = remaining > 10  # Keep some buffer
                
                # Cache rate limit status for 5 minutes
                self.cache_manager.set(rate_limit_cache_key, rate_limit_ok, timeout=300)
                logger.debug(f"Rate limit check: {remaining} requests remaining, ok={rate_limit_ok}")
            except Exception as e:
                logger.warning(f"Rate limit check failed: {e}")
                rate_limit_ok = True  # Assume OK on error
                self.cache_manager.set(rate_limit_cache_key, rate_limit_ok, timeout=60)
        else:
            logger.debug("Rate limit check cached")
        
        return rate_limit_ok
    
    def pullrequests(self):
        """Get pull requests with filtering, sorting, and pagination"""
        start_time = time.time()
        logger.debug(f"/api/pullrequests called from {request.remote_addr}")
        
        # Initialize default values
        page = 1
        per_page = 30
        search_query = ''
        
        # Check authentication
        user, access_token, error_response, error_code = self._check_authentication()
        if error_response:
            return error_response, error_code
        
        # At this point, user and access_token are guaranteed to be non-None
        assert user is not None and access_token is not None
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
            
            logger.debug(f"Parameters - Sort: {sort}, Search: '{search_query}', Page: {page}, Per page: {per_page}")
            if table_sort:
                logger.debug(f"Table sort: {table_sort} {table_sort_direction}")
            
            # Check rate limit
            if not self._check_rate_limit(access_token, user_id):
                logger.warning("Rate limit exceeded")
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'pullrequests': [],
                    'total_count': 0,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': 0,
                    'has_next': False,
                    'has_prev': False,
                    'search_query': search_query
                }), 429
            
            # Generate cache key for pull requests
            cache_params = f"{sort}_{search_query}_{table_sort}_{table_sort_direction}".replace(' ', '_')
            cache_key = self.cache_manager.generate_cache_key(f'pullrequests_{cache_params}', user_id)
            
            # Try to get from cache first
            cached_prs = self.cache_manager.get(cache_key)
            if cached_prs is not None:
                logger.debug("Using cached pull requests data")
                all_pullrequests = cached_prs
            else:
                logger.debug("Fetching fresh pull requests data...")
                
                # Create service and fetch data
                pr_repository = PullRequestRepository(access_token)
                pr_service = PullRequestService(pr_repository)
                
                # Get all pull requests
                all_pullrequests = pr_service.get_all_pull_requests(user_id)
                logger.debug(f"Fetched {len(all_pullrequests)} total pull requests")
                
                # Apply search filter
                if search_query:
                    all_pullrequests = pr_service.filter_pull_requests(all_pullrequests, search_query)
                    logger.debug(f"After search filter: {len(all_pullrequests)} pull requests")
                
                # Apply sorting
                all_pullrequests = pr_service.sort_pull_requests(
                    all_pullrequests, 
                    sort, 
                    table_sort, 
                    table_sort_direction
                )
                
                # Cache the filtered and sorted results for 5 minutes
                self.cache_manager.set(cache_key, all_pullrequests, timeout=300)
            
            # Apply pagination
            pr_service = PullRequestService(None)  # Just for pagination method
            paginated_pullrequests, pagination_info = pr_service.paginate_pull_requests(
                all_pullrequests, page, per_page
            )
            
            # Convert to dictionaries for JSON response
            pullrequests_data = [pr.to_dict() for pr in paginated_pullrequests]
            
            # Log timing and performance info
            elapsed_time = time.time() - start_time
            logger.debug(f"Request completed in {elapsed_time:.2f}s - returned {len(pullrequests_data)} PRs")
            
            response_data = {
                'pullrequests': pullrequests_data,
                'page': pagination_info['page'],
                'per_page': pagination_info['per_page'],
                'total_count': pagination_info['total_count'],
                'total_pages': pagination_info['total_pages'],
                'has_next': pagination_info['has_next'],
                'has_prev': pagination_info['has_prev'],
                'search_query': search_query,
                'sort': sort
            }
            
            # Include table sorting info if present
            if table_sort:
                response_data['table_sort'] = table_sort
                response_data['table_sort_direction'] = table_sort_direction
            
            return jsonify(response_data)
            
        except Exception as e:
            logger.error(f"Error in pullrequests endpoint: {e}")
            return jsonify({
                'error': 'Failed to fetch pull requests',
                'pullrequests': [],
                'total_count': 0,
                'page': page,
                'per_page': per_page,
                'total_pages': 0,
                'has_next': False,
                'has_prev': False,
                'search_query': search_query
            }), 500
    
    def debug_simple_pullrequests(self):
        """Debug endpoint to test simple pull request fetch"""
        user, access_token, error_response, error_code = self._check_authentication()
        if error_response:
            return error_response, error_code
        
        try:
            logger.debug("Debug: Testing simple PR fetch...")
            
            # Create repository and service
            pr_repository = PullRequestRepository(access_token)
            pr_service = PullRequestService(pr_repository)
            
            # Get first few pull requests
            user_id = user.get('id') if user else None
            pullrequests = pr_service.get_all_pull_requests(user_id, max_prs=5)
            
            pullrequests_data = [pr.to_dict() for pr in pullrequests]
            
            logger.debug(f"Debug: Successfully fetched {len(pullrequests_data)} PRs")
            
            return jsonify({
                'success': True,
                'count': len(pullrequests_data),
                'pullrequests': pullrequests_data
            })
            
        except Exception as e:
            logger.error(f"Debug endpoint error: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'pullrequests': []
            }), 500
