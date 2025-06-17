"""
Gist controller with proper error handling and caching
"""
import time
import logging
from flask import Blueprint, request, session, jsonify
from github import Github
from services.gist_service import GistService, GistRepository
from services.cache_service import CacheManager

logger = logging.getLogger(__name__)


class GistController:
    """Controller for gist-related endpoints"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.blueprint = Blueprint('gists', __name__)
        self._register_routes()
    
    def _register_routes(self):
        """Register all gist routes"""
        self.blueprint.add_url_rule('/api/gists', 'gists', self.gists, methods=['GET'])
        self.blueprint.add_url_rule('/api/debug/simple-gists', 'debug_simple_gists', self.debug_simple_gists, methods=['GET'])
    
    def _check_authentication(self):
        """Check if user is authenticated and return user data and access token"""
        if 'user' not in session:
            logger.debug("User not authenticated")
            return None, None, jsonify({'error': 'User not authenticated'}), 401
        
        access_token = session.get('access_token')
        if not access_token:
            logger.debug("No access token found")
            return None, None, jsonify({'error': 'No access token found'}), 401
        
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
                core_remaining = rate_limit.core.remaining
                
                rate_limit_ok = core_remaining > 10  # Require at least 10 requests remaining
                
                # Cache the result for 5 minutes
                self.cache_manager.set(rate_limit_cache_key, rate_limit_ok, timeout=300)
                
                logger.debug(f"Rate limit check: {core_remaining} requests remaining, ok={rate_limit_ok}")
            except Exception as e:
                logger.warning(f"Failed to check rate limit: {e}")
                rate_limit_ok = True  # Assume OK if check fails
        else:
            logger.debug("Rate limit check cached")
        
        return rate_limit_ok
    
    def gists(self):
        """Get gists with filtering, sorting, and pagination"""
        start_time = time.time()
        logger.debug(f"/api/gists called from {request.remote_addr}")
        
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
                return jsonify({
                    'error': 'Rate limit exceeded. Please try again later.',
                    'gists': [],
                    'search_query': search_query,
                    'debug_info': {'rate_limited': True}
                }), 429
            
            logger.debug("Fetching gists using cached method...")
            fetch_start = time.time()
            
            # Get all gists from cache or API
            cache_key = self.cache_manager.generate_cache_key('gists_raw', user_id)
            cached_gist_data = self.cache_manager.get(cache_key)
            
            if cached_gist_data is not None:
                logger.debug(f"Using cached gists data: {len(cached_gist_data)} gists")
                gists = cached_gist_data
            else:
                logger.debug("Cache miss, fetching gists from GitHub API...")
                
                # Create gist service for data fetching
                gist_repository = GistRepository(access_token)
                gist_service = GistService(gist_repository)
                
                # Fetch all gists
                gists = gist_service.get_all_gists(user_id)
                
                # Cache the raw gist data for 30 minutes
                self.cache_manager.set(cache_key, gists, timeout=1800)
                logger.debug(f"Cached {len(gists)} gists for user {user_id}")
            
            # Create gist service for business logic operations
            gist_repository = GistRepository(access_token)
            gist_service = GistService(gist_repository)
            
            # Apply search filter if needed
            if search_query:
                gists = gist_service.filter_gists(gists, search_query)
                logger.debug(f"Filtered to {len(gists)} gists matching '{search_query}'")
            
            # Apply sorting
            gists = gist_service.sort_gists(
                gists, sort=sort, table_sort=table_sort, 
                table_sort_direction=table_sort_direction
            )
            
            # Apply pagination
            paginated_gists, pagination_info = gist_service.paginate_gists(
                gists, page=page, per_page=per_page
            )
            
            # Convert to dictionaries for JSON response
            gist_dicts = [gist.to_dict() for gist in paginated_gists]
            
            fetch_time = time.time() - fetch_start
            total_time = time.time() - start_time
            
            logger.debug(f"Processed {len(paginated_gists)} gists in {fetch_time:.2f}s")
            logger.debug(f"Total processing time: {total_time:.2f}s")
            
            result = {
                'gists': gist_dicts,
                'search_query': search_query,
                'table_sort': table_sort,
                'table_sort_direction': table_sort_direction,
                'debug_info': {
                    'processing_time': total_time,
                    'fetch_time': fetch_time,
                    'gists_total': len(gists),
                    'gists_returned': len(paginated_gists),
                    'cache_enabled': True,
                    'single_cache_strategy': True,
                    'table_sort_applied': bool(table_sort)
                },
                **pagination_info
            }
            
            logger.debug(f"Returning {len(paginated_gists)} gists "
                        f"(page {pagination_info['page']}/{pagination_info['total_pages']})")
            return jsonify(result)
            
        except Exception as e:
            error_msg = f'Failed to fetch gists: {str(e)}'
            logger.error(f"Exception in gists endpoint: {error_msg}")
            return jsonify({
                'error': error_msg,
                'gists': [],
                'search_query': search_query,
                'debug_info': {'error': True, 'error_message': str(e)}
            }), 500
    
    def debug_simple_gists(self):
        """Debug endpoint to test simple gist fetch"""
        user, access_token, error_response, error_code = self._check_authentication()
        if error_response:
            return error_response, error_code
        
        try:
            start_time = time.time()
            github_client = Github(access_token)
            user_obj = github_client.get_user()
            
            # Use simple auto-paginated approach, but limit to 5 gists
            simple_gists = []
            for gist in user_obj.get_gists():
                if len(simple_gists) >= 5:
                    break
                simple_gists.append({
                    'id': gist.id,
                    'description': gist.description,
                    'public': gist.public,
                    'created_at': gist.created_at.isoformat() if gist.created_at else None,
                    'updated_at': gist.updated_at.isoformat() if gist.updated_at else None,
                    'html_url': gist.html_url,
                    'comments': gist.comments,
                    'files': list(gist.files.keys())
                })
            
            end_time = time.time()

            return jsonify({
                'simple_gists': simple_gists,
                'count': len(simple_gists),
                'processing_time': end_time - start_time
            })
            
        except Exception as e:
            error_msg = f'Failed to fetch simple gists: {str(e)}'
            logger.error(f"Exception in debug_simple_gists endpoint: {error_msg}")
            return jsonify({'error': error_msg, 'simple_gists': []}), 500
